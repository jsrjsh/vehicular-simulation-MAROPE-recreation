"""
scripts/queue_loss_forensics.py

Read-only instrumentation for the queue_loss root-cause investigation. Does NOT modify
env/environment.py, agents/*, or scripts/reproduce_paper_sweeps.py. Mirrors evaluate_policy()'s
exact eval loop (same env construction, same action-selection logic, same 5-episode protocol,
same seed offset `seed + 100 + ep`) so the instrumented run is faithful to what actually produced
the reported 5.46%/2.46% numbers, but additionally logs internal env state
(self.rsu_queues, self.active_tasks, self.is_new_task) that evaluate_policy()'s own info dict
does not expose.

Usage: PYTHONPATH=<workspace> python3 scripts/queue_loss_forensics.py
"""
import csv
import os
import sys
import numpy as np
import torch

from env.environment import V2XEnv
from env.config import TASK_TYPES, ACTION_MAP
from agents.d3qn.agent import D3QNAgent
from agents.federated.coordinator import FederatedCoordinator

ENV_MODE = "baseline_recreation"
N_AGENTS = 32
SEED = 0
EPISODES = 5

FIELDS = [
    "policy", "episode", "step", "vehicle_id", "task_arrival", "task_type",
    "selected_action", "nominal_rat", "nominal_rho", "realised_rho",
    "task_data_mb", "task_cpu_cycles", "task_deadline_ms",
    "rsu_id", "queue_before_this_step", "queue_after_aggregation",
    "workload_contributed", "counted_in_queue_aggregation",
    "sinr_db", "transmission_attempted", "transmission_success",
    "latency_ms", "queue_delay_ms_component", "energy_j",
    "queue_loss_event", "queue_loss_denominator_event",
]


def build_ma_rope_agents(checkpoint_path, n_agents, seed):
    """Reconstruct a coordinator matching train_ma_rope()'s construction and load the real
    trained checkpoint from the canonical campaign into every agent (mirrors the fact that
    train_ma_rope keeps one shared-ish set trained together; evaluate_policy uses coord.agents[i]
    per-vehicle with each agent's own trained weights -- but the campaign's saved .pt is only
    agent[0]'s state_dict per get_checkpoint_hash()'s convention). To faithfully reproduce what
    evaluate_policy() actually evaluated, we must reload the SAME coordinator object structure
    used at training time. Since only agent[0]'s weights were persisted to disk (by design in
    train_ma_rope/get_checkpoint_hash), and FedAvg synchronizes all agents to a shared global
    model every 50 steps, loading agent[0]'s weights into every agent is a faithful reconstruction
    of the post-training synchronized state for baseline_recreation MA-ROPE evaluation.
    """
    torch.manual_seed(seed)
    coord = FederatedCoordinator(
        n_agents=n_agents, state_dim=12, action_dim=11,
        buffer_capacity=5000, batch_size=32, target_update_frequency=100,
        replay_mode="prioritized", participation_prob=0.9, seed=seed,
    )
    state_dict = torch.load(checkpoint_path, weights_only=False, map_location="cpu")
    for agent in coord.agents:
        agent.online_net.load_state_dict(state_dict)
        agent.target_net.load_state_dict(state_dict)
        agent.epsilon = agent.epsilon_end  # evaluate=True bypasses epsilon anyway; harmless
    return coord


def run_traced_episode(env, policy_type, coord, episode_idx, writer, seed):
    obs_dict = env.reset(seed=seed + 100 + episode_idx)
    done = False
    step = 0
    while not done:
        step += 1
        action_dict = {}
        for i in range(env.n_vehicles):
            if policy_type == "ma-rope":
                state = obs_dict[i]
                task = env.active_tasks[i]
                is_safety = (task["type"] == "safety")
                action_dict[i] = coord.agents[i].select_action(state, is_safety_task=is_safety, evaluate=True)
            elif policy_type == "alloffload":
                action_dict[i] = 8
            else:
                action_dict[i] = 0

        # Snapshot pre-step state needed for the trace (queue state BEFORE this step's aggregation)
        queue_before = {r: env.rsu_queues[r] for r in range(len(env.rsu_positions))}
        task_arrival = {i: env.is_new_task[i] for i in range(env.n_vehicles)}
        task_snapshot = {i: dict(env.active_tasks[i]) for i in range(env.n_vehicles)}

        next_obs, rewards, dones, infos = env.step(action_dict)
        done = dones["__all__"]

        queue_after = {r: env.rsu_queues[r] for r in range(len(env.rsu_positions))}

        for i in range(env.n_vehicles):
            act_idx = action_dict[i]
            nominal_rat, nominal_rho = ACTION_MAP[act_idx]
            info = infos[i]
            rsu_id = env._get_nearest_rsu(env.positions[i])
            attempted = (nominal_rat > 0 and info["adapted_rho"] > 0.0)
            # This mirrors evaluate_policy()'s exact counting condition (rat > 0 and rho > 0.0
            # using the NOMINAL chosen_rho, not adapted_rho -- reproduced exactly):
            counted_denominator = (info["chosen_rat"] > 0 and info["chosen_rho"] > 0.0)
            queue_loss_event = counted_denominator and (not info["transmission_success"])
            was_aggregated_this_step = (
                nominal_rat > 0 and nominal_rho > 0.0 and
                (env.mode in ["baseline_recreation", "legacy_guide"] or task_arrival[i])
            )
            writer.writerow({
                "policy": policy_type, "episode": episode_idx, "step": step, "vehicle_id": i,
                "task_arrival": task_arrival[i], "task_type": task_snapshot[i]["type"],
                "selected_action": act_idx, "nominal_rat": nominal_rat, "nominal_rho": nominal_rho,
                "realised_rho": info["adapted_rho"],
                "task_data_mb": task_snapshot[i]["data_mb"], "task_cpu_cycles": task_snapshot[i]["cpu_cycles"],
                "task_deadline_ms": task_snapshot[i]["D_ms"],
                "rsu_id": rsu_id, "queue_before_this_step": queue_before[rsu_id],
                "queue_after_aggregation": queue_after[rsu_id],
                "workload_contributed": (nominal_rho if was_aggregated_this_step else 0.0),
                "counted_in_queue_aggregation": was_aggregated_this_step,
                "sinr_db": "", "transmission_attempted": attempted,
                "transmission_success": info["transmission_success"],
                "latency_ms": info["latency_ms"], "queue_delay_ms_component": info["queue_delay_ms"],
                "energy_j": info["energy_j"],
                "queue_loss_event": queue_loss_event,
                "queue_loss_denominator_event": counted_denominator,
            })
        obs_dict = next_obs


def main():
    out_dir = "results/CAMPAIGN_CANONICAL_20260802/forensics"
    os.makedirs(out_dir, exist_ok=True)

    # MA-ROPE: use the REAL trained checkpoint from the validated canonical campaign
    ckpt_path = "results/CAMPAIGN_CANONICAL_20260802/raw/n32/ma-rope_seed0.pt"
    coord = build_ma_rope_agents(ckpt_path, N_AGENTS, SEED)
    env = V2XEnv(n_vehicles=N_AGENTS, scenario="urllc", max_steps=100, seed=SEED, mode=ENV_MODE, policy_type="ma-rope")
    out_path = f"{out_dir}/QUEUE_EVENT_TRACE_MAROPE.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for ep in range(1, EPISODES + 1):
            run_traced_episode(env, "ma-rope", coord, ep, writer, SEED)
    print(f"wrote {out_path}")

    # AllOffload: no coordinator needed
    env2 = V2XEnv(n_vehicles=N_AGENTS, scenario="urllc", max_steps=100, seed=SEED, mode=ENV_MODE, policy_type="alloffload")
    out_path2 = f"{out_dir}/QUEUE_EVENT_TRACE_ALLOFFLOAD.csv"
    with open(out_path2, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for ep in range(1, EPISODES + 1):
            run_traced_episode(env2, "alloffload", None, ep, writer, SEED)
    print(f"wrote {out_path2}")


if __name__ == "__main__":
    main()
