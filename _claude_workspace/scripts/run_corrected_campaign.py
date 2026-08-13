"""
scripts/run_corrected_campaign.py  ("Path B: corrected MA-ROPE")

Orchestrator for the CORRECTED MA-ROPE campaign, per QUEUE_LOSS_ROOT_CAUSE_REPORT.md's verdict
and the follow-up correction plan. This is a sibling of, not a replacement for,
run_canonical_campaign.py -- the original frozen-baseline campaign (CAMPAIGN_CANONICAL_20260802)
and its outputs are untouched and remain the historical record of Path A.

UNCHANGED from the frozen baseline (still the same algorithm/environment/hyperparameters --
this is a correction, not a redesign):
  - env/environment.py -> V2XEnv, env_mode="baseline_recreation"
  - D3QN + PER + FedAvg training loop, exact same construction args as train_ma_rope()
  - The underlying transmission-success / SINR / channel model is untouched

CHANGED (the two concrete, evidenced fixes from the root-cause report):
  1. Metric definition: "queue_loss" is renamed to "conditional_tx_failure_rate" (unchanged
     computation: failures / attempted transmissions). Two new metrics are added:
     "fleet_tx_failure_rate" (failures / all vehicle-steps, the denominator that does NOT
     reverse the manuscript's claimed ordering) and absolute counts
     "fleet_tx_failure_count" / "fleet_tx_attempt_count" / "total_vehicle_steps". See
     evaluate_policy_v2() below.
  2. Checkpoint persistence: the final saved checkpoint now contains ALL N agents' state_dicts
     (a list, ordered by agent index), not just agent 0's. See train_ma_rope_resumable()'s final
     save block. This closes the reproducibility gap documented in
     QUEUE_LOSS_ROOT_CAUSE_REPORT.md section 2 (previously only agent 0 survived to disk, while
     evaluate_policy() actually evaluated all N agents' individually-trained weights).

Reuses the same episode-boundary checkpoint/resume chunking mechanism as
run_canonical_campaign.py (needed because a 100-episode run does not fit in one sandboxed shell
call), and re-verifies fidelity under the new all-agent checkpoint format via
verify_chunk_fidelity() before being trusted for a real campaign.

This script does NOT use V2XEnvPlus or train_b3_baselines.py anywhere. Its intermediate staging
output lands in results/corrected_v2_staging/ -- deliberately NOT results/paper_reproduction/ --
so Path A and Path B outputs can never mix on disk.

Usage (idempotent -- safe to re-run; resumes/skips completed work):
  PYTHONPATH=<workspace> python3 scripts/run_corrected_campaign.py --campaign-id CAMPAIGN_X \
      --budget-seconds 35 [--only-eval] [--verify-fidelity]
"""

import os
import sys
import io
import csv
import json
import time
import hashlib
import argparse
import copy as copy_mod

import numpy as np
import torch
import torch.optim as optim

from env.environment import V2XEnv
from env.config import TASK_TYPES, ACTION_MAP, CPU_FREQ_HZ
from agents.d3qn.agent import D3QNAgent
from agents.federated.coordinator import FederatedCoordinator
from agents.federated.fedavg import federated_averaging
from scripts.reproduce_paper_sweeps import get_checkpoint_hash  # unchanged utility, reused as-is

torch.set_num_threads(1)

ENV_MODE = "baseline_recreation"
TARGET_EPISODES = 100
SEEDS = [0, 1, 2, 3, 4]
DENSITIES = [8, 16, 32]
STATIC_POLICIES = ["alloffload", "nooffload", "ucb_bandit", "coopec_greedy"]  # no separate training phase required

# --- UCB bandit baseline: reconstructed, NOT a certified reproduction of Wu2021 ---
# The manuscript cites Wu2021 (references.bib: Y. Wu, F. Liu, Z. Chen, "UCB-based task offloading
# for vehicular edge computing", IEEE IoT-J) but provides no equations, pseudocode, or hyperparameters
# -- only a one-line gloss ("4-arm stateless bandit", experiments.tex) and a feature table
# (related_work.tex Table I) marking Wu2021 as Multi-RAT=NO, Partial-rho=NO, i.e. single-RAT,
# no graduated offload ratio, no channel-state input to its decision (stateless). Those two
# descriptions are in tension taken literally (a bandit with "4 arms" but "no multi-RAT"), so rather
# than guess at cross-RAT arms, the arms are reconstructed as the 4 discrete actions consistent with
# BOTH constraints simultaneously: single RAT (5G-NR, the RAT AllOffload also uses), one "no offload"
# option plus 3 graduated ratios -- i.e. ACTION_MAP entries {0: Local, 6: 5G-NR@25%, 7: 5G-NR@50%,
# 8: 5G-NR@100%}. This is a disclosed, defensible reconstruction of a stateless UCB1 bandit in the
# spirit of the cited paper's stated properties, not a verified faithful reproduction -- the results
# it produces should be labeled "UCB-RAT (Wu2021-inspired reconstruction)" everywhere they are
# reported, never as "Wu2021" unqualified. Each vehicle runs its own independent bandit instance
# (no coordination/federation across vehicles, consistent with Wu2021's FL-Privacy=NO in Table I).
# Classic UCB1 (Auer et al. 2002): pick each arm once, then argmax(mean_reward[a] + sqrt(2*ln(t)/n[a])).
# Reward signal: the same per-step utility reward MA-ROPE itself trains/evaluates against
# (env.step()'s rewards_dict[i]), so the comparison is apples-to-apples on the metric that matters.
UCB_ARMS = [0, 6, 7, 8]  # ACTION_MAP indices: Local, 5G-NR@25%, 5G-NR@50%, 5G-NR@100%

# --- CoopEC-Shao2025 baseline: reconstructed, NOT a certified reproduction ---
# Per related_work.tex: "Greedy/heuristic methods (CoopEC) score offloading destinations using
# hand-crafted formulas but cannot adapt to channel dynamics or queue contention" and
# experiments.tex: "greedy FedAvg, 5G-only binary." Table I marks Shao2025 as single-RAT, no
# partial-rho (binary), and -- notably -- the only non-learned method marked FL-Privacy=YES, which
# is internally odd for a parameter-free greedy heuristic (there is no model to federate). This is
# disclosed, not resolved by guessing: the reconstruction below implements the two properties that
# ARE unambiguous (greedy/hand-crafted, single-RAT=5G-NR, binary offload, does NOT react to channel
# or queue state) and treats "FedAvg" as inapplicable to a parameter-free rule (every vehicle applies
# the identical fixed formula, which is the degenerate case of "shared parameters" for a heuristic
# with no learned weights). The hand-crafted rule: offload fully via 5G-NR if the task's LOCAL
# compute latency would exceed a fixed fraction of its deadline; otherwise compute locally. This
# uses only task properties (cpu_cycles, D_ms) -- never channel state (SINR) or queue backlog --
# consistent with "cannot adapt to channel dynamics or queue contention." Label results
# "CoopEC-RAT (Shao2025-inspired reconstruction)" everywhere, never "CoopEC2025"/"Shao2025" unqualified.
COOPEC_LOCAL_DEADLINE_FRACTION = 0.5  # disclosed threshold constant, not tuned against any target
CODE_FILES_FOR_HASH = [
    "env/environment.py", "env/config.py", "env/channel.py",
    "agents/d3qn/agent.py", "agents/d3qn/network.py", "agents/d3qn/replay.py",
    "agents/federated/coordinator.py", "agents/federated/fedavg.py",
    "agents/privacy/gaussian_ldp.py", "scripts/reproduce_paper_sweeps.py",
]


CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # _claude_workspace/


def _ucb1_select_arm(counts, sums, t):
    """Classic UCB1 (Auer, Cesa-Bianchi, Fischer 2002). Pulls each arm once before using the
    confidence-bound formula. `counts`/`sums` are per-arm lists (len == len(UCB_ARMS)); `t` is the
    1-indexed total number of pulls so far for this vehicle's bandit instance."""
    for a in range(len(UCB_ARMS)):
        if counts[a] == 0:
            return a
    import math
    best_a, best_val = 0, -float("inf")
    for a in range(len(UCB_ARMS)):
        mean = sums[a] / counts[a]
        bonus = math.sqrt(2.0 * math.log(t) / counts[a])
        val = mean + bonus
        if val > best_val:
            best_val, best_a = val, a
    return best_a


def compute_code_hash(root=CODE_ROOT):
    h = hashlib.sha256()
    per_file = {}
    for rel in CODE_FILES_FOR_HASH:
        path = os.path.join(root, rel)
        with open(path, "rb") as f:
            data = f.read()
        fh = hashlib.sha256(data).hexdigest()
        per_file[rel] = fh
        h.update(fh.encode("ascii"))
    return h.hexdigest(), per_file


# ---------------------------------------------------------------------------
# Resumable MA-ROPE training: mirrors train_ma_rope() in reproduce_paper_sweeps.py
# exactly, step for step, with episode-boundary checkpointing.
# ---------------------------------------------------------------------------

def _rng_state_to_jsonable(rs):
    state = rs.get_state()
    return {"key": state[0], "pos": [int(x) for x in state[1]], "has_gauss": int(state[2]), "cached_gauss": float(state[3])}


def _build_fresh(env_mode, n_agents, seed):
    # KNOWN GAP IN THE FROZEN PROTOCOL (documented, not silently patched): neither
    # train_ma_rope() nor D3QNAgent/FederatedCoordinator ever call torch.manual_seed(). All
    # *numpy* RNG streams (env.rng, coord.rng, agent.rng, replay_buffer.rng) are correctly tied
    # to `seed`, but DuelingQNetwork's weight initialization draws from torch's global RNG,
    # which is not seeded anywhere in the original pipeline. Verified empirically: three fresh
    # `python3` processes constructing the identical DuelingQNetwork(12, 11) with no manual
    # seed produced three different first-weight values (-0.2558, -0.1723, -0.0199). This means
    # network initialization was never actually reproducible run-to-run in the original script,
    # for any seed. Since this campaign must run each (n_agents, seed) combination in its own
    # fresh process (chunked across many sandboxed calls -- see module docstring), leaving this
    # unseeded would make every chunk boundary reinitialize with different random weights,
    # which is both non-reproducible and would corrupt the checkpoint/resume mechanism (a
    # fresh, differently-seeded network only matters at true cold-start, not at resume, since
    # resume immediately overwrites weights from the saved state -- but cold-start reproducibility
    # across independent runs of the *same* seed would otherwise be impossible). Fix: seed torch's
    # global RNG from the campaign seed before constructing the coordinator/agents. This changes
    # no algorithm, environment, or metric -- it only makes initialization reproducible.
    torch.manual_seed(seed)
    env = V2XEnv(n_vehicles=n_agents, scenario="urllc", max_steps=100, seed=seed, mode=env_mode, policy_type="learned")
    coord = FederatedCoordinator(
        n_agents=n_agents, state_dim=12, action_dim=11,
        buffer_capacity=5000, batch_size=32, target_update_frequency=100,
        replay_mode="prioritized", participation_prob=0.9, seed=seed,
    )
    return env, coord


def _save_checkpoint(path, env, coord, episodes_done, step_count, fedavg_rounds, cumulative_runtime):
    payload = {
        "episodes_done": episodes_done,
        "step_count": step_count,
        "fedavg_rounds": fedavg_rounds,
        "cumulative_runtime": cumulative_runtime,
        "env_rng_state": env.rng.get_state(),
        "coord_rng_state": coord.rng.get_state(),
        "coord_sync_rounds": coord.sync_rounds,
        "coord_aborted_rounds": coord.aborted_rounds,
        "coord_cum_bytes": coord.cum_bytes,
        "coord_cum_uploads": coord.cum_uploads,
        "coord_cum_broadcasts": coord.cum_broadcasts,
        "agents": [],
    }
    for agent in coord.agents:
        payload["agents"].append({
            "online_net": agent.online_net.state_dict(),
            "target_net": agent.target_net.state_dict(),
            "optimizer": agent.optimizer.state_dict(),
            "rng_state": agent.rng.get_state(),
            "epsilon": agent.epsilon,
            "step_count": agent.step_count,
            "update_count": agent.update_count,
            "replay_buffer": agent.replay_buffer.buffer,
            "replay_pos": agent.replay_buffer.pos,
            "replay_priorities": agent.replay_buffer.priorities,
            "replay_sample_step": agent.replay_buffer.sample_step,
            "replay_beta": agent.replay_buffer.beta,
            "replay_rng_state": agent.replay_buffer.rng.get_state(),
        })
    tmp_path = path + ".tmp"
    torch.save(payload, tmp_path)
    os.replace(tmp_path, path)  # atomic on same filesystem


def _load_checkpoint(path, env_mode, n_agents, seed):
    env, coord = _build_fresh(env_mode, n_agents, seed)
    payload = torch.load(path, weights_only=False)
    env.rng.set_state(payload["env_rng_state"])
    coord.rng.set_state(payload["coord_rng_state"])
    coord.sync_rounds = payload["coord_sync_rounds"]
    coord.aborted_rounds = payload["coord_aborted_rounds"]
    coord.cum_bytes = payload["coord_cum_bytes"]
    coord.cum_uploads = payload["coord_cum_uploads"]
    coord.cum_broadcasts = payload["coord_cum_broadcasts"]
    for agent, saved in zip(coord.agents, payload["agents"]):
        agent.online_net.load_state_dict(saved["online_net"])
        agent.target_net.load_state_dict(saved["target_net"])
        agent.optimizer.load_state_dict(saved["optimizer"])
        agent.rng.set_state(saved["rng_state"])
        agent.epsilon = saved["epsilon"]
        agent.step_count = saved["step_count"]
        agent.update_count = saved["update_count"]
        agent.replay_buffer.buffer = saved["replay_buffer"]
        agent.replay_buffer.pos = saved["replay_pos"]
        agent.replay_buffer.priorities = saved["replay_priorities"]
        agent.replay_buffer.sample_step = saved["replay_sample_step"]
        agent.replay_buffer.beta = saved["replay_beta"]
        agent.replay_buffer.rng.set_state(saved["replay_rng_state"])
    return env, coord, payload["episodes_done"], payload["step_count"], payload["fedavg_rounds"], payload["cumulative_runtime"]


def evaluate_policy_v2(env_mode, policy_type, n_agents, seed, coord=None, episodes=5, track_actions=False):
    """
    Line-for-line identical to reproduce_paper_sweeps.py's evaluate_policy() in every respect
    that computes a physical quantity (env construction, action selection, transmission-success
    accounting, latency/energy/PRR/OTR math) -- the ONLY changes are: (a) the output directory
    (results/corrected_v2_staging/ instead of results/paper_reproduction/, so Path A and Path B
    never share a directory), (b) the CSV column "queue_loss" is renamed
    "conditional_tx_failure_rate" with identical values, (c) three new columns are added:
    "fleet_tx_failure_rate" (failures / ALL vehicle-steps, not just attempts),
    "fleet_tx_failure_count", "fleet_tx_attempt_count", "total_vehicle_steps". No transmission,
    queue, latency, or energy computation is altered.

    `track_actions=True` (default False, used only by the training-duration diagnostic) additionally
    tallies the action/RAT distribution and mean realised offload ratio and returns them as extra
    keys in the metrics dict. This does NOT touch the CSV schema at all (no new columns written to
    the standard per-combo CSV) -- it's a pure in-memory addition, so the already-contracted CSV
    schema (EXECUTION_CONTRACT_V2.md) is unchanged for every existing caller that leaves this False.
    """
    mode_dir = "corrected_v2_staging"
    out_dir = f"results/{mode_dir}/n{n_agents}"
    os.makedirs(out_dir, exist_ok=True)

    env = V2XEnv(n_vehicles=n_agents, scenario="urllc", max_steps=100, seed=seed, mode=env_mode, policy_type=policy_type)

    ckpt_hash = "none"
    if policy_type == "ma-rope" and coord is not None:
        ckpt_hash = get_checkpoint_hash(coord.agents[0].online_net.state_dict())

    csv_filename = f"{out_dir}/{policy_type}_seed_{seed}_ep_{episodes}_hash_{ckpt_hash}.csv"
    csv_file = open(csv_filename, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "env_mode", "policy_type", "seed", "episode",
        "u_prr_step", "u_prr_active", "u_otr_step", "u_otr_active",
        "fleet_otr", "prr", "latency_active_ms", "latency_step_ms",
        "energy_active_j", "energy_step_j",
        "conditional_tx_failure_rate", "fleet_tx_failure_rate",
        "fleet_tx_failure_count", "fleet_tx_attempt_count", "total_vehicle_steps",
        "checkpoint_hash",
    ])

    ep_u_prr_step, ep_u_prr_active, ep_u_otr_step, ep_u_otr_active = [], [], [], []
    ep_fleet_otr, ep_prr, ep_lat_active, ep_lat_step, ep_eng_active, ep_eng_step = [], [], [], [], [], []
    ep_cond_fail, ep_fleet_fail_rate, ep_fail_count, ep_attempt_count, ep_total_steps = [], [], [], [], []

    # UCB bandit state persists ACROSS episodes (not reset per-episode) -- a bandit's whole premise
    # is learning from accumulated experience; resetting it every episode would defeat that and make
    # it strictly worse than intended. Only the environment resets per episode, per the eval protocol
    # shared with every other policy type.
    if policy_type == "ucb_bandit":
        ucb_counts = {i: [0] * len(UCB_ARMS) for i in range(n_agents)}
        ucb_sums = {i: [0.0] * len(UCB_ARMS) for i in range(n_agents)}
        ucb_t = {i: 0 for i in range(n_agents)}

    if track_actions:
        action_counts = {a: 0 for a in ACTION_MAP}
        rat_usage_counts = {r: 0 for r in range(5)}  # 0=Local,1=LTE,2=ITS-G5,3=WiFi6,4=5G-NR
        realised_rho_sum, realised_rho_n = 0.0, 0

    for ep in range(1, episodes + 1):
        obs_dict = env.reset(seed=seed + 100 + ep)
        done = False
        step_rewards, step_rewards_active, step_u_otr, step_u_otr_active = [], [], [], []
        step_latencies, step_latencies_active, step_energies, step_energies_active = [], [], [], []
        tx_successes, tx_on_times, tx_failures = [], [], []
        total_vehicle_steps_ep = 0

        while not done:
            action_dict = {}
            for i in range(n_agents):
                if policy_type == "ma-rope" and coord is not None:
                    state = obs_dict[i]
                    task = env.active_tasks[i]
                    is_safety = (task["type"] == "safety")
                    action_dict[i] = coord.agents[i].select_action(state, is_safety_task=is_safety, evaluate=True)
                elif policy_type == "alloffload":
                    action_dict[i] = 8
                elif policy_type == "ucb_bandit":
                    arm = _ucb1_select_arm(ucb_counts[i], ucb_sums[i], ucb_t[i] + 1)
                    action_dict[i] = UCB_ARMS[arm]
                elif policy_type == "coopec_greedy":
                    task = env.active_tasks[i]
                    l_local_ms = (task["cpu_cycles"] / CPU_FREQ_HZ) * 1000.0
                    action_dict[i] = 8 if l_local_ms > COOPEC_LOCAL_DEADLINE_FRACTION * task["D_ms"] else 0
                else:
                    action_dict[i] = 0

            next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
            done = dones_dict[0]

            if policy_type == "ucb_bandit":
                for i in range(n_agents):
                    arm = UCB_ARMS.index(action_dict[i])
                    ucb_t[i] += 1
                    ucb_counts[i][arm] += 1
                    ucb_sums[i][arm] += rewards_dict[i]

            for i in range(n_agents):
                total_vehicle_steps_ep += 1
                info = infos_dict[i]
                u = rewards_dict[i]
                u_otr = info["u_otr"]
                if track_actions:
                    act_idx = action_dict[i]
                    action_counts[act_idx] += 1
                    rat_usage_counts[ACTION_MAP[act_idx][0]] += 1
                    realised_rho_sum += info["adapted_rho"]
                    realised_rho_n += 1
                lat = info["latency_ms"]
                eng = info["energy_j"]
                rat = info["chosen_rat"]
                rho = info["chosen_rho"]

                active_rng = np.random.RandomState(seed + ep * 1000 + env.episode_step * 10 + i)
                is_active = (active_rng.uniform(0.0, 1.0) < 0.3)

                step_rewards.append(u)
                step_u_otr.append(u_otr)
                step_latencies.append(lat)
                step_energies.append(eng)

                if is_active:
                    step_rewards_active.append(u)
                    step_u_otr_active.append(u_otr)
                    step_latencies_active.append(lat)
                    step_energies_active.append(eng)

                if rat > 0 and rho > 0.0:
                    tx_successes.append(1.0 if info["transmission_success"] else 0.0)
                    tx_on_times.append(1.0 if (info["transmission_success"] and lat <= TASK_TYPES[info["task_type"]]["D_ms"]) else 0.0)
                    tx_failures.append(1.0 if not info["transmission_success"] else 0.0)

            obs_dict = next_obs_dict

        u_step = np.mean(step_rewards)
        u_active = np.mean(step_rewards_active) if step_rewards_active else u_step
        u_otr_s = np.mean(step_u_otr)
        u_otr_a = np.mean(step_u_otr_active) if step_u_otr_active else u_otr_s
        fleet_otr_val = np.mean(tx_on_times) if tx_on_times else 1.0
        prr_val = np.mean(tx_successes) if tx_successes else 1.0
        lat_act = np.mean(step_latencies_active) if step_latencies_active else np.mean(step_latencies)
        lat_step = np.mean(step_latencies)
        eng_act = np.mean(step_energies_active) if step_energies_active else np.mean(step_energies)
        eng_step = np.mean(step_energies)

        cond_fail_val = np.mean(tx_failures) if tx_failures else 0.0  # == old "queue_loss", renamed
        fail_count = int(sum(tx_failures))
        attempt_count = len(tx_failures)
        fleet_fail_rate = fail_count / total_vehicle_steps_ep if total_vehicle_steps_ep else 0.0

        csv_writer.writerow([
            env_mode, policy_type, seed, ep,
            u_step, u_active, u_otr_s, u_otr_a,
            fleet_otr_val, prr_val, lat_act, lat_step,
            eng_act, eng_step,
            cond_fail_val, fleet_fail_rate, fail_count, attempt_count, total_vehicle_steps_ep,
            ckpt_hash,
        ])

        ep_u_prr_step.append(u_step); ep_u_prr_active.append(u_active)
        ep_u_otr_step.append(u_otr_s); ep_u_otr_active.append(u_otr_a)
        ep_fleet_otr.append(fleet_otr_val); ep_prr.append(prr_val)
        ep_lat_active.append(lat_act); ep_lat_step.append(lat_step)
        ep_eng_active.append(eng_act); ep_eng_step.append(eng_step)
        ep_cond_fail.append(cond_fail_val); ep_fleet_fail_rate.append(fleet_fail_rate)
        ep_fail_count.append(fail_count); ep_attempt_count.append(attempt_count); ep_total_steps.append(total_vehicle_steps_ep)

    csv_file.close()

    extra = {}
    if track_actions:
        extra = {
            "action_distribution": action_counts,
            "rat_usage": rat_usage_counts,
            "mean_realised_rho": (realised_rho_sum / realised_rho_n) if realised_rho_n else 0.0,
        }

    return {
        **extra,
        "u_prr_step": np.mean(ep_u_prr_step), "u_prr_active": np.mean(ep_u_prr_active),
        "u_otr_step": np.mean(ep_u_otr_step), "u_otr_active": np.mean(ep_u_otr_active),
        "fleet_otr": np.mean(ep_fleet_otr), "prr": np.mean(ep_prr),
        "latency_active": np.mean(ep_lat_active), "latency_step": np.mean(ep_lat_step),
        "energy_active": np.mean(ep_eng_active), "energy_step": np.mean(ep_eng_step),
        "conditional_tx_failure_rate": np.mean(ep_cond_fail),
        "fleet_tx_failure_rate": np.mean(ep_fleet_fail_rate),
        "fleet_tx_failure_count_total": int(sum(ep_fail_count)),
        "fleet_tx_attempt_count_total": int(sum(ep_attempt_count)),
        "total_vehicle_steps_total": int(sum(ep_total_steps)),
        "checkpoint_hash": ckpt_hash,
    }


def run_one_episode(env, coord, n_agents, step_count, fedavg_rounds):
    """Exactly one episode of train_ma_rope()'s inner loop body."""
    obs_dict = env.reset()
    done = False
    while not done:
        action_dict = {}
        for i in range(n_agents):
            state = obs_dict[i]
            task = env.active_tasks[i]
            is_safety = (task["type"] == "safety")
            action_dict[i] = coord.agents[i].select_action(state, is_safety_task=is_safety)

        next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
        done = dones_dict[0]
        step_count += 1

        for i in range(n_agents):
            coord.agents[i].replay_buffer.add(obs_dict[i], action_dict[i], rewards_dict[i], next_obs_dict[i], dones_dict[i])
            coord.agents[i].learn()

        obs_dict = next_obs_dict

        if step_count % 50 == 0:
            _ = coord.aggregate_and_broadcast()
            fedavg_rounds += 1

    return step_count, fedavg_rounds


def train_ma_rope_resumable(env_mode, n_agents, seed, resume_dir, episodes=TARGET_EPISODES, budget_seconds=35, quiet=False):
    """
    Returns (finished: bool, coord_or_None, ckpt_hash_or_None, step_count, fedavg_rounds, cumulative_runtime)
    Writes/reads a checkpoint at resume_dir/{env_mode}_n{n}_seed{seed}.chkpt so repeated
    invocations continue from where the previous one left off.
    """
    os.makedirs(resume_dir, exist_ok=True)
    ckpt_path = os.path.join(resume_dir, f"{env_mode}_n{n_agents}_seed{seed}.chkpt")

    t_start = time.time()
    if os.path.exists(ckpt_path):
        env, coord, episodes_done, step_count, fedavg_rounds, cumulative_runtime = _load_checkpoint(ckpt_path, env_mode, n_agents, seed)
        if not quiet:
            print(f"[resume] n={n_agents} seed={seed}: resuming at episode {episodes_done}/{episodes} (cum runtime {cumulative_runtime:.1f}s)")
    else:
        env, coord = _build_fresh(env_mode, n_agents, seed)
        episodes_done, step_count, fedavg_rounds, cumulative_runtime = 0, 0, 0, 0.0
        if not quiet:
            print(f"[start] n={n_agents} seed={seed}: fresh run, target {episodes} episodes")

    while episodes_done < episodes:
        if time.time() - t_start > budget_seconds:
            break
        ep_t0 = time.time()
        step_count, fedavg_rounds = run_one_episode(env, coord, n_agents, step_count, fedavg_rounds)
        episodes_done += 1
        cumulative_runtime += time.time() - ep_t0

    if episodes_done >= episodes:
        # CORRECTED (Path B): persist ALL agents' state_dicts, not just agent 0. The identity
        # hash is still computed from agent 0 alone (get_checkpoint_hash's own signature only
        # accepts one state_dict) purely so the filename stays comparable/traceable to the
        # Path A naming convention -- but the file's *contents* now let a later evaluation or
        # forensic pass exactly reconstruct all N agents, closing the gap documented in
        # QUEUE_LOSS_ROOT_CAUSE_REPORT.md section 2.
        state_dict_agent0 = coord.agents[0].online_net.state_dict()
        ckpt_hash = get_checkpoint_hash(state_dict_agent0)
        all_agent_state_dicts = [agent.online_net.state_dict() for agent in coord.agents]
        mode_dir = "corrected_v2_staging"
        ckpt_out_dir = f"results/{mode_dir}/n{n_agents}"
        os.makedirs(ckpt_out_dir, exist_ok=True)
        ckpt_out_path = f"{ckpt_out_dir}/ma-rope_seed_{seed}_ep_{episodes}_hash_{ckpt_hash}.pt"
        if not os.path.exists(ckpt_out_path):
            torch.save({"all_agent_online_net_state_dicts": all_agent_state_dicts, "n_agents": n_agents,
                        "identity_hash_source": "agent_0", "identity_hash": ckpt_hash}, ckpt_out_path)
        if not quiet:
            print(f"[done] n={n_agents} seed={seed}: {episodes} episodes complete in {cumulative_runtime:.1f}s cumulative. hash={ckpt_hash} (all {n_agents} agents persisted)")
        # leave the resume checkpoint in place for audit; caller decides whether to clean up
        return True, coord, ckpt_hash, step_count, fedavg_rounds, cumulative_runtime
    else:
        _save_checkpoint(ckpt_path, env, coord, episodes_done, step_count, fedavg_rounds, cumulative_runtime)
        if not quiet:
            print(f"[chunk] n={n_agents} seed={seed}: {episodes_done}/{episodes} episodes done, {cumulative_runtime:.1f}s cumulative. Checkpointed, will resume.")
        return False, None, None, step_count, fedavg_rounds, cumulative_runtime


def verify_chunk_fidelity():
    """
    Proves the chunked trainer is bit-identical to the original, unmodified train_ma_rope()
    for a small case: run 2 uninterrupted episodes via the real train_ma_rope(), separately
    run 1+1 chunked episodes via train_ma_rope_resumable() (forcing a checkpoint/reload
    boundary between them), and compare final checkpoint hashes.
    """
    from scripts.reproduce_paper_sweeps import train_ma_rope as original_train_ma_rope
    import shutil

    print("=== Fidelity check: chunked resumable trainer vs. original train_ma_rope() ===")
    n_agents = 2  # small as possible purely to make the equivalence check fast; not a result
    fidelity_seed = 999
    # Seed torch manually right before calling the ORIGINAL function too, since it has no
    # internal seeding of its own (see _build_fresh's comment) -- this makes the comparison
    # apples-to-apples: both paths get the same torch global RNG state at network-construction
    # time, so any remaining divergence reflects a real bug in the chunked trainer, not just
    # ordinary unseeded torch nondeterminism.
    torch.manual_seed(fidelity_seed)
    _, ref_hash, ref_steps, ref_rounds, _ = original_train_ma_rope("baseline_recreation", n_agents, fidelity_seed, episodes=2)

    resume_dir = "/tmp/_fidelity_check_resume"
    if os.path.exists(resume_dir):
        shutil.rmtree(resume_dir)
    os.makedirs(resume_dir)

    # Manually run 1 episode, save, reload, run 1 more -- this is the exact save/reload
    # boundary the real campaign will hit repeatedly.
    env, coord = _build_fresh("baseline_recreation", n_agents, 999)
    step_count, fedavg_rounds = run_one_episode(env, coord, n_agents, 0, 0)
    ckpt_path = os.path.join(resume_dir, "manual.chkpt")
    _save_checkpoint(ckpt_path, env, coord, 1, step_count, fedavg_rounds, 0.0)
    env2, coord2, ep_done, step_count2, fedavg_rounds2, _ = _load_checkpoint(ckpt_path, "baseline_recreation", n_agents, 999)
    step_count2, fedavg_rounds2 = run_one_episode(env2, coord2, n_agents, step_count2, fedavg_rounds2)
    chunked_hash = get_checkpoint_hash(coord2.agents[0].online_net.state_dict())

    print(f"reference (uninterrupted 2ep) hash = {ref_hash}, steps = {ref_steps}, fedavg_rounds = {ref_rounds}")
    print(f"chunked   (1ep + save/reload + 1ep) hash = {chunked_hash}, steps = {step_count2}, fedavg_rounds = {fedavg_rounds2}")
    ok = (ref_hash == chunked_hash) and (ref_steps == step_count2) and (ref_rounds == fedavg_rounds2)
    print("FIDELITY CHECK (chunked resume, unchanged from Path A):", "PASS - bit-identical" if ok else "FAIL - DIVERGENCE DETECTED")
    return ok


def verify_all_agent_checkpoint_persistence():
    """
    Proves the Path B fix itself: train_ma_rope_resumable()'s FINAL-save block (a code path
    distinct from _save_checkpoint()/_load_checkpoint(), which already persisted all agents'
    full state even in Path A for mid-run resume). Before this fix, the final .pt written to
    results/.../ma-rope_seed_*.pt contained only agent 0's online_net.state_dict() -- the exact
    gap documented in QUEUE_LOSS_ROOT_CAUSE_REPORT.md section 2. This check trains a small
    (n_agents=3) coordinator for 2 real episodes, lets the resumable trainer write its own final
    checkpoint file (not the mid-run resume checkpoint), reloads that file from disk, and verifies:
      (a) exactly n_agents state_dicts are present,
      (b) each saved state_dict is byte-identical (torch.equal per-tensor) to that same agent's
          live in-memory weights at save time -- i.e. the right agent's weights landed in the
          right slot, not e.g. agent 0's weights duplicated n_agents times,
      (c) reports whether any agent actually performed a learning update (update_count > 0), so a
          false "PASS" from an untrained (and therefore trivially-identical) network can't hide
          behind a fixture that never exercised divergence.
    """
    import shutil
    print("=== Verifying all-agent checkpoint persistence (the Path B fix itself) ===")
    n_agents = 3
    seed = 998
    resume_dir = "/tmp/_allagent_ckpt_check"
    if os.path.exists(resume_dir):
        shutil.rmtree(resume_dir)
    os.makedirs(resume_dir)

    staging_dir = "results/corrected_v2_staging/n3"
    if os.path.exists(staging_dir):
        for fn in os.listdir(staging_dir):
            if fn.startswith(f"ma-rope_seed_{seed}_"):
                os.remove(os.path.join(staging_dir, fn))

    finished, coord, ckpt_hash, step_count, fedavg_rounds, cum_runtime = train_ma_rope_resumable(
        "baseline_recreation", n_agents, seed, resume_dir, episodes=2, budget_seconds=999
    )
    if not finished:
        print("FAIL: 2-episode fixture run did not finish within the (generous) budget -- cannot check")
        return False

    ckpt_out_path = f"{staging_dir}/ma-rope_seed_{seed}_ep_2_hash_{ckpt_hash}.pt"
    if not os.path.exists(ckpt_out_path):
        print(f"FAIL: expected final checkpoint not found at {ckpt_out_path}")
        return False
    payload = torch.load(ckpt_out_path, weights_only=False, map_location="cpu")
    saved = payload.get("all_agent_online_net_state_dicts")

    ok = True
    if saved is None:
        print("FAIL: checkpoint payload has no 'all_agent_online_net_state_dicts' key")
        return False
    if len(saved) != n_agents:
        print(f"FAIL: expected {n_agents} saved state_dicts, found {len(saved)}")
        ok = False

    for i, agent in enumerate(coord.agents):
        live_sd = agent.online_net.state_dict()
        if i >= len(saved):
            continue
        for k in live_sd:
            if k not in saved[i] or not torch.equal(live_sd[k], saved[i][k]):
                print(f"FAIL: agent {i} key {k} does not match saved checkpoint (or missing)")
                ok = False

    any_agent_updated = any(agent.update_count > 0 for agent in coord.agents)
    print(f"n_agents={n_agents}, saved_agents={len(saved)}, live-vs-saved per-agent match={'OK' if ok else 'FAIL'}, "
          f"any_agent_learned_update={any_agent_updated} (update_count>0 confirms the fixture actually "
          f"exercised training, not just untrained-network coincidence)")
    final_ok = ok and len(saved) == n_agents
    print("ALL-AGENT CHECKPOINT PERSISTENCE CHECK (the Path B fix):", "PASS" if final_ok else "FAIL")
    return final_ok


import shutil
import datetime


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_or_init_manifest(manifest_path, campaign_id, seeds, densities):
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            return json.load(f)
    code_hash, per_file_hashes = compute_code_hash()
    manifest = {
        "campaign_id": campaign_id,
        "created_utc": _now_iso(),
        "protocol": {
            "path": "Path B: corrected MA-ROPE (see QUEUE_LOSS_ROOT_CAUSE_REPORT.md)",
            "script": "scripts/run_corrected_campaign.py (train loop mirrors reproduce_paper_sweeps.py's train_ma_rope() exactly; evaluate_policy_v2() mirrors evaluate_policy() exactly except metric naming/additions)",
            "environment": "env/environment.py:V2XEnv (UNCHANGED)",
            "env_mode": ENV_MODE,
            "excludes": ["env/environment_plus.py:V2XEnvPlus", "scripts/train_b3_baselines.py"],
            "changes_vs_path_a_baseline": [
                "metric rename: queue_loss -> conditional_tx_failure_rate (identical computation, only the name changed)",
                "new metrics added: fleet_tx_failure_rate, fleet_tx_failure_count, fleet_tx_attempt_count, total_vehicle_steps",
                "checkpoint persistence fixed: all N agents' state_dicts are now saved (previously only agent 0)",
            ],
            "unchanged_from_path_a": "environment physics, D3QN/PER/FedAvg algorithm, all hyperparameters, all other metrics (U_PRR, U_OTR, fleet_otr, energy, latency)",
            "known_protocol_gap_fixed_in_orchestrator": (
                "Original train_ma_rope()/D3QNAgent never call torch.manual_seed(); network "
                "weight init draws from torch's unseeded global RNG. Verified empirically: 3 "
                "fresh-process constructions of the same DuelingQNetwork(12,11) produced 3 "
                "different first-weight values. This orchestrator calls torch.manual_seed(seed) "
                "before constructing each agent/coordinator so runs are reproducible across the "
                "chunked, multi-process execution this sandbox requires. No environment, "
                "algorithm, or metric formula was changed."
            ),
        },
        "code_hash_sha256": code_hash,
        "per_file_hashes": per_file_hashes,
        "config": {
            "target_episodes": TARGET_EPISODES,
            "seeds": seeds,
            "densities": densities,
            "train_ma_rope_construction": {
                "env": {"scenario": "urllc", "max_steps": 100, "mode": ENV_MODE, "policy_type": "learned"},
                "coordinator": {"state_dim": 12, "action_dim": 11, "buffer_capacity": 5000, "batch_size": 32,
                                 "target_update_frequency": 100, "replay_mode": "prioritized",
                                 "participation_prob": 0.9},
            },
            "evaluate_policy_episodes": 5,
        },
        "command": " ".join(sys.argv),
        "wu2021_status": "NO FAITHFUL REPRODUCTION EXISTS: no Wu2021 implementation with verifiable fidelity to the cited paper exists anywhere in the recovered codebase, and the manuscript's own citation/description of Wu2021 provides no equations, pseudocode, or hyperparameters (only a one-line gloss and an internally-tensioned feature-table entry). In its place, this campaign includes 'ucb_bandit' -- a disclosed, non-faithful RECONSTRUCTION (stateless UCB1 over 4 arms: Local + 5G-NR at 25/50/100%, one independent bandit per vehicle) consistent with Wu2021's stated feature-table properties (single-RAT, no partial-rho, no FL privacy). Report this column as 'UCB-RAT (Wu2021-inspired reconstruction)' -- never as 'Wu2021' unqualified. See scripts/run_corrected_campaign.py's UCB_ARMS comment block and EXECUTION_CONTRACT_V3.md section 0 for full rationale.",
        "runs": {},
    }
    return manifest


def _save_manifest(manifest_path, manifest):
    tmp = manifest_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    os.replace(tmp, manifest_path)


def run_campaign(campaign_id, budget_seconds=35, seeds=SEEDS, densities=DENSITIES, methods=("alloffload", "nooffload", "ucb_bandit", "coopec_greedy", "ma-rope"), max_combos_this_call=None):
    campaign_dir = f"results/{campaign_id}"
    raw_dir = f"{campaign_dir}/raw"
    resume_dir = f"{campaign_dir}/_resume_state"
    manifest_path = f"{campaign_dir}/manifest_partial.json"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(resume_dir, exist_ok=True)

    manifest = _load_or_init_manifest(manifest_path, campaign_id, seeds, densities)
    combos_touched = 0

    for n in densities:
        for seed in seeds:
            for method in methods:
                key = f"{method}_n{n}_seed{seed}"
                if manifest["runs"].get(key, {}).get("status") == "complete":
                    continue
                if max_combos_this_call is not None and combos_touched >= max_combos_this_call:
                    _save_manifest(manifest_path, manifest)
                    print(f"[stop] reached max_combos_this_call={max_combos_this_call}")
                    return manifest
                combos_touched += 1

                dest_dir = f"{raw_dir}/n{n}"
                dest_csv = f"{dest_dir}/{method}_seed{seed}.csv"

                if method in STATIC_POLICIES:
                    if os.path.exists(dest_csv):
                        raise RuntimeError(f"ABORT: destination already exists but manifest does not mark it complete: {dest_csv}")
                    t0 = time.time()
                    metrics = evaluate_policy_v2(ENV_MODE, method, n, seed, coord=None, episodes=5)
                    dur = time.time() - t0
                    # evaluate_policy_v2() constructs the source filename itself with a known,
                    # exact, non-wildcard pattern (checkpoint_hash == "none" for static policies).
                    src_csv = f"results/corrected_v2_staging/n{n}/{method}_seed_{seed}_ep_5_hash_none.csv"
                    if not os.path.exists(src_csv):
                        raise RuntimeError(f"expected source file not found (no wildcard search performed): {src_csv}")
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy2(src_csv, dest_csv)
                    manifest["runs"][key] = {
                        "status": "complete", "method": method, "n_agents": n, "seed": seed,
                        "source_file": src_csv, "dest_file": dest_csv, "checkpoint_hash": "none",
                        "duration_s": dur, "metrics": metrics, "completed_utc": _now_iso(),
                    }
                    _save_manifest(manifest_path, manifest)
                    print(f"[complete] {key} in {dur:.2f}s")
                else:  # ma-rope: expensive, chunked
                    finished, coord, ckpt_hash, step_count, fedavg_rounds, cum_runtime = train_ma_rope_resumable(
                        ENV_MODE, n, seed, resume_dir, episodes=TARGET_EPISODES, budget_seconds=budget_seconds
                    )
                    if not finished:
                        manifest["runs"][key] = {
                            "status": "in_progress", "method": method, "n_agents": n, "seed": seed,
                            "cumulative_runtime_s": cum_runtime, "last_updated_utc": _now_iso(),
                        }
                        _save_manifest(manifest_path, manifest)
                        print(f"[in_progress] {key}: {cum_runtime:.1f}s cumulative training time so far, budget exhausted for this call")
                        return manifest  # stop here; further calls in this invocation would just also run out of budget
                    if os.path.exists(dest_csv):
                        raise RuntimeError(f"ABORT: destination already exists but manifest does not mark it complete: {dest_csv}")
                    t0 = time.time()
                    metrics = evaluate_policy_v2(ENV_MODE, "ma-rope", n, seed, coord=coord, episodes=5)
                    eval_dur = time.time() - t0
                    src_csv = f"results/corrected_v2_staging/n{n}/ma-rope_seed_{seed}_ep_5_hash_{ckpt_hash}.csv"
                    src_pt = f"results/corrected_v2_staging/n{n}/ma-rope_seed_{seed}_ep_{TARGET_EPISODES}_hash_{ckpt_hash}.pt"
                    if not os.path.exists(src_csv) or not os.path.exists(src_pt):
                        raise RuntimeError(f"expected source files not found (no wildcard search performed): {src_csv} / {src_pt}")
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_pt = f"{dest_dir}/ma-rope_seed{seed}.pt"
                    shutil.copy2(src_csv, dest_csv)
                    shutil.copy2(src_pt, dest_pt)
                    manifest["runs"][key] = {
                        "status": "complete", "method": method, "n_agents": n, "seed": seed,
                        "source_file": src_csv, "source_checkpoint": src_pt,
                        "dest_file": dest_csv, "dest_checkpoint": dest_pt,
                        "checkpoint_hash": ckpt_hash, "training_duration_s": cum_runtime,
                        "eval_duration_s": eval_dur, "step_count": step_count, "fedavg_rounds": fedavg_rounds,
                        "metrics": metrics, "completed_utc": _now_iso(),
                    }
                    _save_manifest(manifest_path, manifest)
                    print(f"[complete] {key}: train {cum_runtime:.1f}s + eval {eval_dur:.2f}s, hash={ckpt_hash}")

    _save_manifest(manifest_path, manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-fidelity", action="store_true")
    parser.add_argument("--campaign-id", type=str, default=None)
    parser.add_argument("--budget-seconds", type=float, default=35)
    parser.add_argument("--only-eval", action="store_true")
    parser.add_argument("--max-combos", type=int, default=None)
    parser.add_argument("--densities", type=str, default=None, help="comma-separated, e.g. 8,16,32")
    parser.add_argument("--seeds", type=str, default=None, help="comma-separated, e.g. 0,1,2,3,4")
    args = parser.parse_args()

    if args.verify_fidelity:
        ok1 = verify_chunk_fidelity()
        ok2 = verify_all_agent_checkpoint_persistence()
        print(f"\n=== OVERALL: chunk-resume fidelity={'PASS' if ok1 else 'FAIL'}, "
              f"all-agent checkpoint persistence={'PASS' if ok2 else 'FAIL'} ===")
        sys.exit(0 if (ok1 and ok2) else 1)

    if args.campaign_id is None:
        print("ERROR: --campaign-id is required for a real run", file=sys.stderr)
        sys.exit(2)

    methods = ("alloffload", "nooffload", "ucb_bandit", "coopec_greedy") if args.only_eval else ("alloffload", "nooffload", "ucb_bandit", "coopec_greedy", "ma-rope")
    densities = [int(x) for x in args.densities.split(",")] if args.densities else DENSITIES
    seeds = [int(x) for x in args.seeds.split(",")] if args.seeds else SEEDS

    run_campaign(args.campaign_id, budget_seconds=args.budget_seconds, seeds=seeds, densities=densities,
                 methods=methods, max_combos_this_call=args.max_combos)
