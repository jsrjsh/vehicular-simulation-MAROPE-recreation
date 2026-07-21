import os
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from env.environment_plus import V2XEnvPlus
from agents.d3qn.agent import D3QNAgent
import torch

def evaluate_scenario(env, policy_name, num_episodes=50):
    if policy_name == "shared_d3qn":
        agent = D3QNAgent(state_dim=20, action_dim=11, seed=42)
        agent.load("checkpoints_shared/best.pt")
        agent.epsilon = 0.0 # Deterministic evaluation
    metrics = {
        "success": [],
        "latency_all": [],
        "latency_success": [],
        "energy": [],
        "reward": [],
        "queue": [],
        "Q_pos_count": 0,
        "total_slots": 0,
        "class_success": {1: [], 2: [], 3: []},
        "class_ratio": {1: [], 2: [], 3: []} # T_i / D_i
    }
    
    queue_ts = []
    
    for ep in range(num_episodes):
        obs = env.reset(seed=42 + ep)
        dones = {"__all__": False}
        ep_q = []
        
        while not dones["__all__"]:
            actions = {}
            for i in range(env.n_vehicles):
                is_safety = (obs[i][11] == 1.0)
                if policy_name == "random":
                    actions[i] = np.random.choice([0, 4, 5, 6, 7, 8, 9, 10]) if is_safety else np.random.choice(11)
                elif policy_name == "always_local":
                    actions[i] = 0
                elif policy_name == "always_lte":
                    actions[i] = 4 if is_safety else 5
                elif policy_name == "always_5g":
                    actions[i] = 10
                elif policy_name == "shared_d3qn":
                    is_safety = (obs[i][11] == 1.0)
                    actions[i] = agent.select_action(obs[i], is_safety_task=is_safety, evaluate=True)
            
            obs, rewards, dones, infos = env.step(actions)
            
            ep_q.append(env.Q_t)
            metrics["total_slots"] += 1
            if env.Q_t > 0:
                metrics["Q_pos_count"] += 1
                
            for i in range(env.n_vehicles):
                if infos[i]["has_task"]:
                    S_i = infos[i]["S_i"]
                    T_i = infos[i]["T_i"]
                    E_i = infos[i]["E_i"]
                    
                    c_id = 1 if obs[i][11] == 1.0 else (2 if obs[i][12] == 1.0 else 3)
                    D_i = 0.1 if c_id == 1 else (0.5 if c_id == 2 else 1.0)
                    
                    metrics["success"].append(S_i)
                    metrics["latency_all"].append(T_i)
                    if S_i == 1.0:
                        metrics["latency_success"].append(T_i)
                    metrics["energy"].append(E_i)
                    metrics["reward"].append(rewards[i])
                    
                    metrics["class_success"][c_id].append(S_i)
                    metrics["class_ratio"][c_id].append(T_i / D_i)
                    
        queue_ts.extend(ep_q)
        metrics["queue"].extend(ep_q)
        
    return {
        "success_rate": np.mean(metrics["success"]),
        "latency_all": np.mean(metrics["latency_all"]),
        "latency_succ": np.mean(metrics["latency_success"]) if len(metrics["latency_success"])>0 else 0,
        "energy": np.mean(metrics["energy"]),
        "reward": np.mean(metrics["reward"]),
        "q_mean": np.mean(metrics["queue"]),
        "q_p95": np.percentile(metrics["queue"], 95),
        "q_max": np.max(metrics["queue"]),
        "q_pos_frac": metrics["Q_pos_count"] / metrics["total_slots"],
        "class_success": {k: np.mean(v) for k,v in metrics["class_success"].items()},
        "class_ratio": {k: np.mean(v) for k,v in metrics["class_ratio"].items()},
        "class_ratio_raw": metrics["class_ratio"],
        "queue_ts": queue_ts
    }

def main():
    policies = ["random", "always_local", "always_lte", "always_5g", "shared_d3qn"]
    
    # Exact mathematical workload calculation:
    # E[L] = 0.65 * 1e6 + 0.20 * 5e6 + 0.15 * 15e6 = 3.9e6 cycles
    # E[tasks/slot] = 16 vehicles * 0.3 probability = 4.8 tasks/slot
    # W_vehicle_mean = 4.8 * 3.9e6 = 18.72e6 cycles/slot
    # W_bg_mean = 5e6 cycles/slot
    # W_total_mean = 23.72e6 cycles/slot
    # f_mec = W_total_mean / (u * 0.1)
    # Scenario B (u=0.75): f_mec = 23.72e6 / 0.075 = 316.27e6 = 0.316e9
    # Scenario C (u=0.95): f_mec = 23.72e6 / 0.095 = 249.68e6 = 0.250e9
    scenarios = {
        "Scenario A (Underloaded)": V2XEnvPlus(n_vehicles=16, seed=42, f_mec=50e9, bg_workload_enabled=False),
        "Scenario B (Moderate)": V2XEnvPlus(n_vehicles=16, seed=42, f_mec=0.316e9, bg_workload_enabled=True),
        "Scenario C (Heavy)": V2XEnvPlus(n_vehicles=16, seed=42, f_mec=0.250e9, bg_workload_enabled=True)
    }
    
    results = {}
    
    for s_name, env in scenarios.items():
        print(f"\n--- Running {s_name} ---")
        results[s_name] = {}
        for p in policies:
            print(f"  Evaluating {p}...")
            res = evaluate_scenario(env, p, num_episodes=50)
            results[s_name][p] = res
            
    # Save JSON metrics (exclude raw arrays for size)
    clean_results = {}
    for s in results:
        clean_results[s] = {}
        for p in results[s]:
            clean_results[s][p] = {k: v for k,v in results[s][p].items() if k not in ["class_ratio_raw", "queue_ts"]}
            
    with open("scenario_metrics.json", "w") as f:
        json.dump(clean_results, f, indent=4)
        
    # Plot Queue Over Time
    fig, axes = plt.subplots(3, 1, figsize=(12, 12))
    for i, s_name in enumerate(scenarios.keys()):
        for p in policies:
            # plot first 500 steps (5 episodes) for clarity
            axes[i].plot(results[s_name][p]["queue_ts"][:500], label=p)
        axes[i].set_title(s_name + " - Queue Backlog (First 500 steps)")
        axes[i].set_ylabel("Queue (Cycles)")
        axes[i].legend()
        
    plt.tight_layout()
    plt.savefig("/Users/aryaveersingh/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/queue_backlog_scenarios.png")
    
    # Plot Ti/Di for Always 5G in Scenario B
    fig, ax = plt.subplots(figsize=(8, 6))
    data = [
        results["Scenario B (Moderate)"]["always_5g"]["class_ratio_raw"][1],
        results["Scenario B (Moderate)"]["always_5g"]["class_ratio_raw"][2],
        results["Scenario B (Moderate)"]["always_5g"]["class_ratio_raw"][3]
    ]
    ax.boxplot(data, tick_labels=["Safety", "Info", "Compute"])
    ax.set_title("Latency/Deadline Ratio for Always-5G in Scenario B")
    ax.set_ylabel("T_i / D_i")
    ax.axhline(1.0, color='r', linestyle='--', label='Deadline')
    ax.legend()
    plt.savefig("/Users/aryaveersingh/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/latency_deadline_ratio.png")
    print("\nEvaluation complete. Plots and metrics saved.")

if __name__ == "__main__":
    main()
