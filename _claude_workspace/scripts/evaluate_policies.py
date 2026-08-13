import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

from env.environment_plus import V2XEnvPlus
from agents.d3qn.agent import D3QNAgent

def evaluate_policy(env, policy_name, agent=None, episodes=20):
    metrics = {
        "success": [],
        "latency_all": [],
        "latency_success": [],
        "energy": [],
        "reward": [],
        "queue": [],
        "action_dist_by_class": {
            "Safety": {0:0, 1:0, 2:0}, # Local, LTE, 5G
            "Info": {0:0, 1:0, 2:0},
            "Compute": {0:0, 1:0, 2:0}
        }
    }
    
    queue_timeseries = []
    
    for ep in range(episodes):
        obs = env.reset(seed=42 + ep*100)
        dones = {"__all__": False}
        ep_queue = []
        
        while not dones["__all__"]:
            actions = {}
            for i in range(env.n_vehicles):
                is_safety = (obs[i][11] == 1.0)
                is_info = (obs[i][12] == 1.0)
                is_compute = (obs[i][13] == 1.0)
                
                if policy_name == "random":
                    actions[i] = np.random.choice([0, 4, 5, 6, 7, 8, 9, 10]) if is_safety else np.random.choice(11)
                elif policy_name == "always_local":
                    actions[i] = 0
                elif policy_name == "always_lte":
                    actions[i] = 4 if is_safety else 5
                elif policy_name == "always_5g":
                    actions[i] = 10
                elif policy_name == "shared_d3qn":
                    actions[i] = agent.select_action(obs[i], is_safety_task=is_safety, evaluate=True)
                
            obs, rewards, dones, infos = env.step(actions)
            ep_queue.append(env.Q_t)
            
            for i in range(env.n_vehicles):
                if infos[i]["has_task"]:
                    S_i = infos[i]["S_i"]
                    T_i = infos[i]["T_i"]
                    E_i = infos[i]["E_i"]
                    R_i = rewards[i]
                    
                    metrics["success"].append(S_i)
                    metrics["energy"].append(E_i)
                    metrics["reward"].append(R_i)
                    metrics["latency_all"].append(T_i)
                    if S_i == 1.0:
                        metrics["latency_success"].append(T_i)
                        
                    eff_act = infos[i]["effective_action"]
                    
                    if obs[i][11] == 1.0:
                        task_class = "Safety"
                    elif obs[i][12] == 1.0:
                        task_class = "Info"
                    else:
                        task_class = "Compute"
                        
                    if eff_act == 0:
                        metrics["action_dist_by_class"][task_class][0] += 1
                    elif 1 <= eff_act <= 5:
                        metrics["action_dist_by_class"][task_class][1] += 1
                    else:
                        metrics["action_dist_by_class"][task_class][2] += 1
                        
        metrics["queue"].append(np.mean(ep_queue))
        queue_timeseries.append(ep_queue)
        
    avg_queue_over_time = np.mean(queue_timeseries, axis=0).tolist()
    
    # Normalize action dists
    norm_action_dist = {}
    for c, counts in metrics["action_dist_by_class"].items():
        total = sum(counts.values())
        if total > 0:
            norm_action_dist[c] = {k: v/total for k,v in counts.items()}
        else:
            norm_action_dist[c] = counts

    return {
        "success_rate": np.mean(metrics["success"]),
        "mean_latency_all": np.mean(metrics["latency_all"]),
        "mean_latency_success": np.mean(metrics["latency_success"]) if len(metrics["latency_success"]) > 0 else 0.0,
        "mean_energy": np.mean(metrics["energy"]),
        "mean_reward": np.mean(metrics["reward"]),
        "mean_queue": np.mean(metrics["queue"]),
        "action_dist_by_class": norm_action_dist,
        "queue_timeseries": avg_queue_over_time
    }

def run_diagnostics():
    env = V2XEnvPlus(n_vehicles=16, seed=42)
    policies = ["random", "always_local", "always_lte", "always_5g", "shared_d3qn"]
    
    results = {}
    
    agent = None
    if os.path.exists("checkpoints_shared/best.pt"):
        agent = D3QNAgent(state_dim=20, action_dim=11, seed=42)
        agent.load("checkpoints_shared/best.pt")
        print("Loaded Shared D3QN checkpoint.")
    else:
        print("WARNING: Shared D3QN checkpoint not found. D3QN policy will act randomly.")
        agent = D3QNAgent(state_dim=20, action_dim=11, seed=42)
        
    for p in policies:
        print(f"Evaluating {p}...")
        res = evaluate_policy(env, p, agent=agent, episodes=50)
        results[p] = res
        print(f"  Success: {res['success_rate']:.3f} | Reward: {res['mean_reward']:.3f}")
        
    with open("results_diagnostics.json", "w") as f:
        json.dump(results, f, indent=4)
        
    # Plot Queue Over Time
    plt.figure(figsize=(10, 6))
    for p in policies:
        plt.plot(results[p]["queue_timeseries"], label=p)
    plt.title("Average Queue Backlog Over Time")
    plt.xlabel("Step")
    plt.ylabel("Queue Backlog (Cycles)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("/home/researcher/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/queue_backlog.png")
    
    # Plot Action Dist for D3QN
    d3qn_dist = results["shared_d3qn"]["action_dist_by_class"]
    labels = ["Safety", "Info", "Compute"]
    local_vals = [d3qn_dist[l][0] for l in labels]
    lte_vals = [d3qn_dist[l][1] for l in labels]
    _5g_vals = [d3qn_dist[l][2] for l in labels]
    
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(x - width, local_vals, width, label='Local')
    ax.bar(x, lte_vals, width, label='LTE')
    ax.bar(x + width, _5g_vals, width, label='5G')
    
    ax.set_ylabel('Selection Frequency')
    ax.set_title('Shared D3QN Action Distribution by Task Class')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    plt.savefig("/home/researcher/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/action_distribution.png")

if __name__ == "__main__":
    run_diagnostics()
