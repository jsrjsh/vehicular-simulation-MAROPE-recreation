"""
scripts/speed_sweep_eval.py

Genuine, validated replacement for the fabricated vehicle-speed-sweep figures (paper Figs. 3, 4, 6:
Utility/Latency/PRR vs. Vehicle Speed). Original figures plotted 6 methods including MADDPG,
Wu2021, Shao2025, GA+DQN-Yun2022 -- all already established as fabricated/duplicated in
BASELINE_TABLE_INTEGRITY_FINDING.md. This script re-evaluates only the three methods with real,
loadable artifacts: MA-ROPE (using the validated CAMPAIGN_CORRECTED_20260803 N=8 checkpoints,
env_mode="baseline_recreation"), AllOffload, and NoOffload.

Method: identical eval protocol to evaluate_policy_v2() in run_corrected_campaign.py (same env
construction, same action selection, same active-task/on-time/PRR accounting), with ONE addition:
immediately after env.reset(), vehicle speeds are overridden to a constant value (the swept
"vehicle speed" x-axis) instead of the environment's default per-vehicle uniform(20,38) draw.
Nothing else about the physics, channel model, or policy is touched.

Energy is deliberately NOT collected/plotted here -- per ENERGY_METRIC_DECISION.md, Energy is
invalid under baseline_recreation mode regardless of vehicle speed (the formula itself, not the
speed distribution, is broken), so no re-run at any speed makes it reportable.

Usage: PYTHONPATH=. python3 scripts/speed_sweep_eval.py
"""
import os
import csv
import numpy as np
import torch

import torch as _torch

from env.environment import V2XEnv
from env.config import TASK_TYPES
from scripts.run_corrected_campaign import _build_fresh


def load_ma_rope_coord(ckpt_path, env_mode, n_agents, seed):
    """Final campaign checkpoints store only online-net state dicts per agent (see
    run_corrected_campaign.py's train_ma_rope_resumable() final-save block) -- no target net,
    optimizer, replay buffer, or RNG state, since none of those are needed for evaluate=True
    (greedy) inference."""
    _, coord = _build_fresh(env_mode, n_agents, seed)
    payload = _torch.load(ckpt_path, weights_only=False)
    assert payload["n_agents"] == n_agents
    for agent, state_dict in zip(coord.agents, payload["all_agent_online_net_state_dicts"]):
        agent.online_net.load_state_dict(state_dict)
        agent.online_net.eval()
    return coord

torch.set_num_threads(1)

ENV_MODE = "baseline_recreation"
N_AGENTS = 8
SEEDS = [0, 1, 2, 3, 4]
SPEEDS_KMH = [20, 25, 30, 35, 40, 45, 50, 55, 60]
EPISODES_PER_SPEED = 5
CKPT_DIR = "../results/CAMPAIGN_CORRECTED_20260803/raw/n8"
OUT_CSV = "../results/speed_sweep_corrected/speed_sweep_results.csv"

METHODS = ["ma-rope", "alloffload", "nooffload"]


def run_episodes(env_mode, policy_type, n_agents, seed, coord, speed_kmh, episodes):
    u_otr_active_list, lat_active_list, prr_list = [], [], []
    for ep in range(1, episodes + 1):
        env = V2XEnv(n_vehicles=n_agents, scenario="urllc", max_steps=100,
                     seed=seed, mode=env_mode,
                     policy_type=("learned" if policy_type == "ma-rope" else policy_type))
        obs_dict = env.reset(seed=seed + 100 + ep)
        env.speeds[:] = float(speed_kmh)  # fix vehicle speed for this sweep point; nothing else touches self.speeds after reset()

        done = False
        step_u_otr_active = []
        step_lat_active = []
        tx_successes = []

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
                u_otr = info["u_otr"]
                lat = info["latency_ms"]
                rat = info["chosen_rat"]
                rho = info["chosen_rho"]

                active_rng = np.random.RandomState(seed + ep * 1000 + env.episode_step * 10 + i)
                is_active = (active_rng.uniform(0.0, 1.0) < 0.3)
                if is_active:
                    step_u_otr_active.append(u_otr)
                    step_lat_active.append(lat)

                if rat > 0 and rho > 0.0:
                    tx_successes.append(1.0 if info["transmission_success"] else 0.0)

            obs_dict = next_obs_dict

        u_otr_active_list.append(np.mean(step_u_otr_active) if step_u_otr_active else 0.0)
        lat_active_list.append(np.mean(step_lat_active) if step_lat_active else 0.0)
        prr_list.append(np.mean(tx_successes) if tx_successes else 1.0)

    return {
        "u_otr_active": float(np.mean(u_otr_active_list)),
        "latency_active_ms": float(np.mean(lat_active_list)),
        "prr": float(np.mean(prr_list)),
    }


def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    rows = []

    for seed in SEEDS:
        coord = None
        if "ma-rope" in METHODS:
            ckpt_path = f"{CKPT_DIR}/ma-rope_seed{seed}.pt"
            coord = load_ma_rope_coord(ckpt_path, ENV_MODE, N_AGENTS, seed)

        for method in METHODS:
            use_coord = coord if method == "ma-rope" else None
            for speed in SPEEDS_KMH:
                metrics = run_episodes(ENV_MODE, method, N_AGENTS, seed, use_coord, speed, EPISODES_PER_SPEED)
                row = {"method": method, "seed": seed, "speed_kmh": speed, **metrics}
                rows.append(row)
                print(f"[done] {method} seed={seed} speed={speed}: "
                      f"u_otr_active={metrics['u_otr_active']:.4f} "
                      f"lat={metrics['latency_active_ms']:.1f}ms prr={metrics['prr']:.4f}")

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "seed", "speed_kmh", "u_otr_active", "latency_active_ms", "prr"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
