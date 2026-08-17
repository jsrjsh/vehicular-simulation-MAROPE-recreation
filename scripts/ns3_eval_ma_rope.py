"""
scripts/ns3_eval_ma_rope.py

Evaluates a trained MA-ROPE checkpoint (from CAMPAIGN_LATENCY_FIX_20260815,
retrained under the isolated log10-latency fix) against the real ns-3 + SUMO
co-simulation backend (Ns3SumoV2XEnv), computing the same Fleet OTR / PRR /
latency metrics evaluate_policy_v2() computes for the pure-Python campaigns,
so the numbers are directly comparable.

This is NEW, UNVERIFIED code -- it needs the real ns3gym/ns-3 toolchain to
run (not available in this environment), so it has not been executed
end-to-end. Whoever runs this first should sanity-check the raw per-step
output against a hand-traced example before trusting aggregate numbers,
same discipline as everything else tonight.

Known approximations, disclosed rather than silently assumed:
1. Task deadline is NOT in the C++ side's BuildExtraInfo() JSON -- only
   task_type (string). Deadlines are reconstructed via TASK_DEADLINE_MS
   below, which must stay in sync with env/config.py::TASK_TYPES and
   v2x_environment.h's GetSafetyTask()/GetInfotainmentTask()/GetComputeTask()
   (100/500/1000 ms respectively -- verified matching both sources
   2026-08-16). If either side's deadlines ever change, this hardcoded map
   must change too, or Fleet OTR classification will silently be wrong.
2. Ns3SumoV2XEnv.active_tasks is a dead, hardcoded {"type": "safety"} that
   the C++ side never updates -- do NOT read it. is_safety_task for each
   agent's action selection is instead tracked from the PREVIOUS step's
   infos[i]["task_type"] (task type is only knowable retroactively, after a
   step returns). For the very first action of each episode, there is no
   prior info yet; this defaults to is_safety_task=True (a disclosed
   approximation matching the 65% safety-task majority in the URLLC mix,
   not a measured value).

Usage: PYTHONPATH=. python3 scripts/ns3_eval_ma_rope.py --n_vehicles 8 --seed 0
(run from _claude_workspace, or wherever ns3gym + the compiled ns-3 engine
are reachable -- see NS3_SUMO_STATUS.md for setup)
"""
import argparse
import csv
import sys
import os

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_claude_workspace"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "maro_pe"))

from env.ns3_sumo_env import Ns3SumoV2XEnv
from scripts.run_corrected_campaign import _build_fresh

TASK_DEADLINE_MS = {"safety": 100.0, "infotainment": 500.0, "compute": 1000.0}

CKPT_DIR_TEMPLATE = os.path.join(os.path.dirname(__file__), "..", "_claude_workspace", "results", "CAMPAIGN_LATENCY_FIX_20260815", "raw", "n{n}")
ENV_MODE = "baseline_recreation"
EPISODES = 5


def load_ma_rope_coord(ckpt_path, env_mode, n_agents, seed):
    _, coord = _build_fresh(env_mode, n_agents, seed)
    payload = torch.load(ckpt_path, weights_only=False)
    assert payload["n_agents"] == n_agents
    for agent, state_dict in zip(coord.agents, payload["all_agent_online_net_state_dicts"]):
        agent.online_net.load_state_dict(state_dict)
        agent.online_net.eval()
    return coord


def run_episode(env, coord, n_agents, last_task_type):
    """Runs one episode against the ns-3 backend. `last_task_type` is a dict
    of agent_id -> task_type string, carried IN and OUT across episodes so
    the is_safety_task approximation (see module docstring) only guesses on
    the very first step of the very first episode, not every episode."""
    obs = env.reset()
    done = False

    tx_successes, tx_on_times = [], []
    step_u_otr_active = []

    while not done:
        action_dict = {}
        for i in range(n_agents):
            is_safety = last_task_type.get(i, "safety") == "safety"
            action_dict[i] = coord.agents[i].select_action(
                obs[i], is_safety_task=is_safety, evaluate=True
            )

        obs, rewards, dones, infos = env.step(action_dict)
        done = dones.get("__all__", False)

        for i in range(n_agents):
            info = infos[i]
            if "task_type" not in info:
                continue  # ns3gym not connected / mocked step, nothing real to record
            last_task_type[i] = info["task_type"]

            rat = info.get("chosen_rat", 0)
            rho = info.get("adapted_rho", 0.0)
            if rat > 0 and rho > 0.0:
                success = bool(info.get("transmission_success", False))
                lat = float(info.get("latency_ms", 0.0))
                deadline = TASK_DEADLINE_MS[info["task_type"]]
                tx_successes.append(1.0 if success else 0.0)
                tx_on_times.append(1.0 if (success and lat <= deadline) else 0.0)

            step_u_otr_active.append(float(info.get("u_otr", 0.0)))

    fleet_otr = float(np.mean(tx_on_times)) if tx_on_times else 1.0
    prr = float(np.mean(tx_successes)) if tx_successes else 1.0
    u_otr = float(np.mean(step_u_otr_active)) if step_u_otr_active else 0.0
    return {"fleet_otr": fleet_otr, "prr": prr, "u_otr_active": u_otr}, last_task_type


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_vehicles", type=int, required=True, choices=[8, 16, 32])
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--episodes", type=int, default=EPISODES)
    args = parser.parse_args()

    ckpt_path = f"{CKPT_DIR_TEMPLATE.format(n=args.n_vehicles)}/ma-rope_seed{args.seed}.pt"
    print(f"Loading checkpoint: {ckpt_path}")
    coord = load_ma_rope_coord(ckpt_path, ENV_MODE, args.n_vehicles, args.seed)

    print(f"Connecting to ns-3 OpenGym backend (n_vehicles={args.n_vehicles})...")
    env = Ns3SumoV2XEnv(n_vehicles=args.n_vehicles, max_steps=200, start_sim=True)

    last_task_type = {}
    ep_results = []
    for ep in range(args.episodes):
        result, last_task_type = run_episode(env, coord, args.n_vehicles, last_task_type)
        print(f"  episode {ep}: fleet_otr={result['fleet_otr']:.4f} "
              f"prr={result['prr']:.4f} u_otr_active={result['u_otr_active']:.4f}")
        ep_results.append(result)

    env.close()

    out_path = f"../results/ns3_eval_n{args.n_vehicles}_seed{args.seed}.csv"
    with open(os.path.join(os.path.dirname(__file__), "..", "_claude_workspace", out_path), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["episode", "fleet_otr", "prr", "u_otr_active"])
        writer.writeheader()
        for ep, r in enumerate(ep_results):
            writer.writerow({"episode": ep, **r})

    means = {k: float(np.mean([r[k] for r in ep_results])) for k in ep_results[0]}
    print(f"\nMean over {args.episodes} episodes: {means}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
