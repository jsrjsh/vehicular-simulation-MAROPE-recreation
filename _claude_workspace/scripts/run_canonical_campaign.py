"""
scripts/run_canonical_campaign.py

Orchestrator for the frozen canonical MA-ROPE reproduction campaign.

FROZEN PROTOCOL (per explicit instruction, not modified by this file):
  - env/environment.py -> V2XEnv
  - env_mode = "baseline_recreation"
  - Training/eval math mirrors scripts/reproduce_paper_sweeps.py's train_ma_rope() and
    evaluate_policy() EXACTLY (same env construction args, same FederatedCoordinator
    construction args, same per-step logic, same FedAvg trigger). evaluate_policy() is
    imported and called UNMODIFIED. train_ma_rope() itself cannot be used unmodified because
    this sandbox caps every shell call at ~45s and a single 100-episode training run takes on
    the order of tens of minutes (measured: N=8 -> ~18.4s/episode). train_ma_rope() has no
    resume hook, so its training loop is reproduced here verbatim, with episode-boundary
    checkpointing added purely for wall-clock chunking. Fidelity is verified separately
    (see verify_chunk_fidelity()) by proving a chunked 1+1-episode run reaches the exact same
    checkpoint hash as an uninterrupted 2-episode call to the real train_ma_rope().

This script does NOT use V2XEnvPlus or train_b3_baselines.py anywhere.

Usage (idempotent -- safe to re-run; resumes/skips completed work):
  PYTHONPATH=<workspace> python3 scripts/run_canonical_campaign.py --campaign-id CAMPAIGN_X \
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
from env.config import TASK_TYPES
from agents.d3qn.agent import D3QNAgent
from agents.federated.coordinator import FederatedCoordinator
from agents.federated.fedavg import federated_averaging
from scripts.reproduce_paper_sweeps import evaluate_policy, get_checkpoint_hash

torch.set_num_threads(1)

ENV_MODE = "baseline_recreation"
TARGET_EPISODES = 100
SEEDS = [0, 1, 2, 3, 4]
DENSITIES = [8, 16, 32]
STATIC_POLICIES = ["alloffload", "nooffload"]  # no training required
CODE_FILES_FOR_HASH = [
    "env/environment.py", "env/config.py", "env/channel.py",
    "agents/d3qn/agent.py", "agents/d3qn/network.py", "agents/d3qn/replay.py",
    "agents/federated/coordinator.py", "agents/federated/fedavg.py",
    "agents/privacy/gaussian_ldp.py", "scripts/reproduce_paper_sweeps.py",
]


CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # _claude_workspace/


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
        state_dict = coord.agents[0].online_net.state_dict()
        ckpt_hash = get_checkpoint_hash(state_dict)
        mode_dir = "paper_reproduction" if env_mode == "baseline_recreation" else "physically_corrected"
        ckpt_out_dir = f"results/{mode_dir}/n{n_agents}"
        os.makedirs(ckpt_out_dir, exist_ok=True)
        ckpt_out_path = f"{ckpt_out_dir}/ma-rope_seed_{seed}_ep_{episodes}_hash_{ckpt_hash}.pt"
        if not os.path.exists(ckpt_out_path):
            torch.save(state_dict, ckpt_out_path)
        if not quiet:
            print(f"[done] n={n_agents} seed={seed}: {episodes} episodes complete in {cumulative_runtime:.1f}s cumulative. hash={ckpt_hash}")
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
    print("FIDELITY CHECK:", "PASS - bit-identical" if ok else "FAIL - DIVERGENCE DETECTED")
    return ok


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
            "script": "scripts/reproduce_paper_sweeps.py (train_ma_rope / evaluate_policy, imported/mirrored unmodified)",
            "environment": "env/environment.py:V2XEnv",
            "env_mode": ENV_MODE,
            "excludes": ["env/environment_plus.py:V2XEnvPlus", "scripts/train_b3_baselines.py"],
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
        "wu2021_status": "NOT INCLUDED: no Wu2021 baseline implementation exists anywhere in the recovered codebase (grep across all .py files for 'wu2021'/'wu_2021' found zero matches). Not canonical/functional; excluded per instruction.",
        "runs": {},
    }
    return manifest


def _save_manifest(manifest_path, manifest):
    tmp = manifest_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    os.replace(tmp, manifest_path)


def run_campaign(campaign_id, budget_seconds=35, seeds=SEEDS, densities=DENSITIES, methods=("alloffload", "nooffload", "ma-rope"), max_combos_this_call=None):
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
                    metrics = evaluate_policy(ENV_MODE, method, n, seed, coord=None, episodes=5)
                    dur = time.time() - t0
                    # evaluate_policy() constructs the source filename itself with a known,
                    # exact, non-wildcard pattern (checkpoint_hash == "none" for static policies).
                    src_csv = f"results/paper_reproduction/n{n}/{method}_seed_{seed}_ep_5_hash_none.csv"
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
                    metrics = evaluate_policy(ENV_MODE, "ma-rope", n, seed, coord=coord, episodes=5)
                    eval_dur = time.time() - t0
                    src_csv = f"results/paper_reproduction/n{n}/ma-rope_seed_{seed}_ep_5_hash_{ckpt_hash}.csv"
                    src_pt = f"results/paper_reproduction/n{n}/ma-rope_seed_{seed}_ep_{TARGET_EPISODES}_hash_{ckpt_hash}.pt"
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
        ok = verify_chunk_fidelity()
        sys.exit(0 if ok else 1)

    if args.campaign_id is None:
        print("ERROR: --campaign-id is required for a real run", file=sys.stderr)
        sys.exit(2)

    methods = ("alloffload", "nooffload") if args.only_eval else ("alloffload", "nooffload", "ma-rope")
    densities = [int(x) for x in args.densities.split(",")] if args.densities else DENSITIES
    seeds = [int(x) for x in args.seeds.split(",")] if args.seeds else SEEDS

    run_campaign(args.campaign_id, budget_seconds=args.budget_seconds, seeds=seeds, densities=densities,
                 methods=methods, max_combos_this_call=args.max_combos)
