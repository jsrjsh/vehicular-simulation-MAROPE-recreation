import torch
import numpy as np
import pandas as pd
import argparse
import sys
import csv
import glob
sys.path.append('.')

from agents.d3qn.agent import D3QNAgent
from env.environment_plus import V2XEnvPlus
from scripts.train_b3_baselines import Evaluator

def extract_decision_boundaries():
    df = pd.read_csv("analysis/QUEUE_SENSITIVITY_RAW.csv")
    df["Mode"] = df["ModelPath"].apply(lambda x: x.split("/")[1].split("_")[0])
    df["Config"] = df["ModelPath"].apply(lambda x: "Candidate_" + x.split("/")[1].split("_")[2] if "Candidate" in x else "Baseline")
    
    df_fb = df[(df["Mode"] == "fedavg") & (df["Config"] == "Candidate_B")]
    
    # Average across all agents/seeds to get the global decision boundary per scenario
    avg_q = df_fb.groupby(["Scenario", "Queue"])["DeltaQ_5G_Loc"].mean().reset_index()
    
    q_switch = {}
    for scen in avg_q["Scenario"].unique():
        s_data = avg_q[avg_q["Scenario"] == scen].sort_values("Queue")
        # Find first queue where DeltaQ_5G_Loc <= 0
        switch_q = None
        for _, row in s_data.iterrows():
            if row["DeltaQ_5G_Loc"] <= 0:
                switch_q = row["Queue"]
                break
        q_switch[scen] = switch_q
        
    return q_switch

def extract_empirical_queues_and_shift(mode="fedavg", config="Candidate_B", seed=222, congestion_multiplier=1.0):
    env = V2XEnvPlus(n_vehicles=16, seed=seed, f_mec=0.316e9, bg_workload_enabled=True,
                     w_s=0.0, w_t=0.0, w_e=0.0, reward_type="piecewise")
    
    env.task_prob = 0.3 * congestion_multiplier
    
    agents = []
    ckpt_dir = f"checkpoints_b33b/{mode}_{config}_seed_{seed}"
    for i in range(16):
        agent = D3QNAgent(state_dim=20, action_dim=11, seed=seed)
        agent.online_net.load_state_dict(torch.load(f"{ckpt_dir}/agent_{i}.pt", map_location="cpu"))
        agent.online_net.eval()
        agents.append(agent)
        
    queue_log = []
    action_counts = {a: 0 for a in range(11)}
    total_actions = 0
    
    action_log = []
    
    for ep in range(10):
        obs = env.reset(seed=seed + ep)
        done = False
        while not done:
            actions = {}
            for i in range(16):
                # Log queue (feature index 1 * Q_max)
                q_val = obs[i][1] * env.Q_max
                queue_log.append(q_val)
                
                with torch.no_grad():
                    device = next(agents[i].online_net.parameters()).device
                    state_tensor = torch.FloatTensor(obs[i]).unsqueeze(0).to(device)
                    q_values = agents[i].online_net(state_tensor).cpu().numpy()[0]
                    act = np.argmax(q_values)
                    actions[i] = act
                    action_log.append(act)
                    action_counts[act] += 1
                    total_actions += 1
                    
            obs, _, done, _ = env.step(actions)
            done = done["__all__"]
            
    act_dist = {a: count / total_actions for a, count in action_counts.items()}
    return queue_log, action_log, act_dist

if __name__ == "__main__":
    print("--- 1. Extracting Decision Boundaries ---")
    boundaries = extract_decision_boundaries()
    for k, v in boundaries.items():
        print(f"Scenario: {k:<20} | Q_switch: {v/1e6 if v is not None else '>100'} M")
        
    print("\n--- 2. Extracting Empirical Queues (Nominal) ---")
    # We will log seed 222 for nominal
    nominal_queues, nominal_actions, nominal_dist = extract_empirical_queues_and_shift(congestion_multiplier=1.0)
    print(f"Nominal 5G Ratio: {sum([nominal_dist[a] for a in range(6, 11)]) * 100:.1f}%")
    print(f"Nominal Local Ratio: {nominal_dist[0] * 100:.1f}%")
    
    print("\n--- 3. Distribution Shift (Heavy Congestion x3) ---")
    shifted_queues, shifted_actions, shifted_dist = extract_empirical_queues_and_shift(congestion_multiplier=3.33)
    print(f"Shifted 5G Ratio: {sum([shifted_dist[a] for a in range(6, 11)]) * 100:.1f}%")
    print(f"Shifted Local Ratio: {shifted_dist[0] * 100:.1f}%")
    
    # Save queues to CSV for histogram plotting later if needed
    pd.DataFrame({"Queue": nominal_queues, "Action": nominal_actions}).to_csv("analysis/empirical_queues_nominal.csv", index=False)
    pd.DataFrame({"Queue": shifted_queues, "Action": shifted_actions}).to_csv("analysis/empirical_queues_shifted.csv", index=False)
    print("\nQueue logs saved to analysis/empirical_queues_*.csv")
