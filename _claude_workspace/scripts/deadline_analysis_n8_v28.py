"""
scripts/deadline_analysis_n8_v28.py

Real replacement for Table 5 (tab:deadline_analysis, "Compact Per-Message-Type
Deadline Analysis"). The existing table was computed before the log10-latency
and Jakes-fading fixes and has never been rerun under corrected physics --
flagged during the v28 manuscript pass. This script reruns the deep N=8
safety-validation-style evaluation under the corrected checkpoints
(CAMPAIGN_PHYSICS_FIX_20260818), breaking down PRR/OTR/latency by task type
(safety/infotainment/compute), using the SAME 5-seed methodology as the rest
of the corrected campaign tables (not attempting to replicate the older
table's bespoke single-seed/200-step/2000m-road protocol, since cloning an
oddball historical setup while also changing physics would conflate two
different changes).
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
N_AGENTS = 8
SEEDS = [0, 1, 2, 3, 4]
EPISODES = 5
CKPT_DIR = "../results/CAMPAIGN_PHYSICS_FIX_20260818/raw/n8"
OUT_CSV = "../results/CAMPAIGN_PHYSICS_FIX_20260818/deadline_analysis_n8_results.csv"


def load_ma_rope_coord(ckpt_path, env_mode, n_agents, seed):
    _, coord = _build_fresh(env_mode, n_agents, seed)
    payload = torch.load(ckpt_path, weights_only=False)
    assert payload["n_agents"] == n_agents
    for agent, state_dict in zip(coord.agents, payload["all_agent_online_net_state_dicts"]):
        agent.online_net.load_state_dict(state_dict)
        agent.online_net.eval()
    return coord


def run_eval(env_mode, n_agents, seed, coord, episodes):
    by_type = {t: {"success": [], "on_time": [], "latency": []} for t in TASK_TYPES}
    for ep in range(1, episodes + 1):
        env = V2XEnv(n_vehicles=n_agents, scenario="urllc", max_steps=100,
                     seed=seed, mode=env_mode, policy_type="learned")
        obs_dict = env.reset(seed=seed + 100 + ep)
        done = False

        while not done:
            action_dict = {}
            for i in range(n_agents):
                state = obs_dict[i]
                task = env.active_tasks[i]
                is_safety = (task["type"] == "safety")
                action_dict[i] = coord.agents[i].select_action(state, is_safety_task=is_safety, evaluate=True)

            next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
            done = dones_dict[0]

            for i in range(n_agents):
                info = infos_dict[i]
                rat = info["chosen_rat"]
                rho = info["chosen_rho"]
                if rat > 0 and rho > 0.0:
                    t_type = info["task_type"]
                    lat = info["latency_ms"]
                    success = info["transmission_success"]
                    by_type[t_type]["success"].append(1.0 if success else 0.0)
                    by_type[t_type]["on_time"].append(1.0 if (success and lat <= TASK_TYPES[t_type]["D_ms"]) else 0.0)
                    if success:
                        by_type[t_type]["latency"].append(lat)

            obs_dict = next_obs_dict

    return by_type


def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    rows = []
    for seed in SEEDS:
        coord = load_ma_rope_coord(f"{CKPT_DIR}/ma-rope_seed{seed}.pt", ENV_MODE, N_AGENTS, seed)
        by_type = run_eval(ENV_MODE, N_AGENTS, seed, coord, EPISODES)
        for t_type, d in by_type.items():
            prr = np.mean(d["success"]) if d["success"] else float("nan")
            otr = np.mean(d["on_time"]) if d["on_time"] else float("nan")
            mean_lat = np.mean(d["latency"]) if d["latency"] else float("nan")
            n_attempts = len(d["success"])
            rows.append({
                "seed": seed, "task_type": t_type, "prr": prr, "otr": otr,
                "mean_latency_ms": mean_lat, "n_attempts": n_attempts,
            })
            print(f"seed={seed} {t_type}: PRR={prr:.4f} OTR={otr:.4f} lat={mean_lat:.1f}ms n={n_attempts}")

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["seed", "task_type", "prr", "otr", "mean_latency_ms", "n_attempts"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
