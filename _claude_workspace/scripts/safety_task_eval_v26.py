"""
scripts/safety_task_eval.py

Genuine replacement for Table XI (Safety-Task Delivery at N=32). The manuscript's prior version
had MADDPG/Yun2022/Wu2021 rows identical to MA-ROPE's own row (fabricated duplicates, see
BASELINE_TABLE_INTEGRITY_FINDING.md); those are dropped rather than reconstructed here since no
safety-task-only breakdown exists in CORRECTED_BASELINE_RESULTS.csv (only aggregate PRR/OTR were
logged by run_corrected_campaign.py). This script computes the safety-task-only PRR/OTR directly
by filtering env.active_tasks[i]["type"] == "safety" at N=32, using the same validated
CAMPAIGN_CORRECTED_20260803 checkpoints (MA-ROPE) / static policy (AllOffload), 5 seeds, 5
episodes each -- same eval protocol as evaluate_policy_v2(), narrowed to the safety task subset.
"""
import os
import csv
import numpy as np
import torch

from env.environment import V2XEnv
from env.config import TASK_TYPES
from scripts.run_corrected_campaign import _build_fresh

torch.set_num_threads(1)

ENV_MODE = "baseline_recreation"
N_AGENTS = 32
SEEDS = [0, 1, 2, 3, 4]
EPISODES = 5
CKPT_DIR = "../results/CAMPAIGN_PHYSICS_FIX_20260818/raw/n32"
OUT_CSV = "../results/CAMPAIGN_PHYSICS_FIX_20260818/safety_task_results.csv"


def load_ma_rope_coord(ckpt_path, env_mode, n_agents, seed):
    _, coord = _build_fresh(env_mode, n_agents, seed)
    payload = torch.load(ckpt_path, weights_only=False)
    assert payload["n_agents"] == n_agents
    for agent, state_dict in zip(coord.agents, payload["all_agent_online_net_state_dicts"]):
        agent.online_net.load_state_dict(state_dict)
        agent.online_net.eval()
    return coord


def run_safety_eval(env_mode, policy_type, n_agents, seed, coord, episodes):
    safety_prr_list, safety_otr_list = [], []
    for ep in range(1, episodes + 1):
        env = V2XEnv(n_vehicles=n_agents, scenario="urllc", max_steps=100,
                     seed=seed, mode=env_mode,
                     policy_type=("learned" if policy_type == "ma-rope" else policy_type))
        obs_dict = env.reset(seed=seed + 100 + ep)
        done = False
        safety_tx_success, safety_tx_on_time = [], []

        while not done:
            action_dict = {}
            for i in range(n_agents):
                if policy_type == "ma-rope":
                    state = obs_dict[i]
                    task = env.active_tasks[i]
                    is_safety = (task["type"] == "safety")
                    action_dict[i] = coord.agents[i].select_action(state, is_safety_task=is_safety, evaluate=True)
                elif policy_type == "alloffload":
                    action_dict[i] = 8
                else:
                    action_dict[i] = 0

            next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
            done = dones_dict[0]

            for i in range(n_agents):
                info = infos_dict[i]
                rat = info["chosen_rat"]
                rho = info["chosen_rho"]
                if rat > 0 and rho > 0.0 and info["task_type"] == "safety":
                    lat = info["latency_ms"]
                    success = info["transmission_success"]
                    safety_tx_success.append(1.0 if success else 0.0)
                    safety_tx_on_time.append(1.0 if (success and lat <= TASK_TYPES["safety"]["D_ms"]) else 0.0)

            obs_dict = next_obs_dict

        safety_prr_list.append(np.mean(safety_tx_success) if safety_tx_success else float("nan"))
        safety_otr_list.append(np.mean(safety_tx_on_time) if safety_tx_on_time else float("nan"))

    return {
        "safety_prr": float(np.nanmean(safety_prr_list)),
        "safety_otr": float(np.nanmean(safety_otr_list)),
    }


def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    rows = []
    for seed in SEEDS:
        coord = load_ma_rope_coord(f"{CKPT_DIR}/ma-rope_seed{seed}.pt", ENV_MODE, N_AGENTS, seed)
        m = run_safety_eval(ENV_MODE, "ma-rope", N_AGENTS, seed, coord, EPISODES)
        rows.append({"method": "ma-rope", "seed": seed, **m})
        print("ma-rope", seed, m)

        m2 = run_safety_eval(ENV_MODE, "alloffload", N_AGENTS, seed, None, EPISODES)
        rows.append({"method": "alloffload", "seed": seed, **m2})
        print("alloffload", seed, m2)

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "seed", "safety_prr", "safety_otr"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
