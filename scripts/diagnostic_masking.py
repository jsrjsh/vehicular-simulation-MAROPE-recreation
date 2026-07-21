import os
import json
import numpy as np
from collections import defaultdict
from env.environment_plus import V2XEnvPlus
from agents.d3qn.agent import D3QNAgent
import torch

class MaskedAgent:
    def __init__(self, agent, mask_Q=False, mask_T=False):
        self.agent = agent
        self.mask_Q = mask_Q
        self.mask_T = mask_T
        
    def select_action(self, obs, is_safety_task=False, evaluate=True):
        masked_obs = np.copy(obs)
        if self.mask_Q:
            masked_obs[1] = 0.0
        if self.mask_T:
            masked_obs[2] = 0.0
            
        return self.agent.select_action(masked_obs, is_safety_task, evaluate)

def run_queue_analysis(env, agent, num_episodes=20):
    print("\n--- Queue-Conditioned Action Analysis ---")
    action_counts = {
        "Q_zero": {0: 0, 1: 0, 2: 0},
        "Q_low": {0: 0, 1: 0, 2: 0},
        "Q_medium": {0: 0, 1: 0, 2: 0},
        "Q_high": {0: 0, 1: 0, 2: 0}
    }
    
    Q_MAX_CYCLES = env.Q_max
    
    for ep in range(num_episodes):
        obs = env.reset(seed=100 + ep)
        dones = {"__all__": False}
        
        while not dones["__all__"]:
            actions = {}
            for i in range(env.n_vehicles):
                is_safety = (obs[i][11] == 1.0)
                actions[i] = agent.select_action(obs[i], is_safety_task=is_safety, evaluate=True)
                
            obs, rewards, dones, infos = env.step(actions)
            
            for i in range(env.n_vehicles):
                if infos[i]["has_task"]:
                    # obs[i][1] is Q_t / Q_max BEFORE taking the action
                    q_val = obs[i][1] * Q_MAX_CYCLES
                    eff_act = infos[i]["effective_action"]
                    
                    act_cat = 0 if eff_act == 0 else (1 if 1 <= eff_act <= 5 else 2)
                    
                    if q_val == 0:
                        bucket = "Q_zero"
                    elif q_val < 5e6:
                        bucket = "Q_low"
                    elif q_val < 20e6:
                        bucket = "Q_medium"
                    else:
                        bucket = "Q_high"
                        
                    action_counts[bucket][act_cat] += 1

    print("Queue Regime | Local | LTE | 5G")
    print("-" * 35)
    for bucket in ["Q_zero", "Q_low", "Q_medium", "Q_high"]:
        counts = action_counts[bucket]
        total = sum(counts.values())
        if total > 0:
            l_pct = counts[0] / total
            lte_pct = counts[1] / total
            g_pct = counts[2] / total
            print(f"{bucket:>12} | {l_pct*100:4.1f}% | {lte_pct*100:4.1f}% | {g_pct*100:4.1f}% (N={total})")
        else:
            print(f"{bucket:>12} |  N/A  |  N/A  |  N/A  (N=0)")
            
    p_local_high = action_counts["Q_high"][0] / sum(action_counts["Q_high"].values()) if sum(action_counts["Q_high"].values()) > 0 else 0
    p_local_zero = action_counts["Q_zero"][0] / sum(action_counts["Q_zero"].values()) if sum(action_counts["Q_zero"].values()) > 0 else 0
    print(f"\nP(Local | Q_t high) = {p_local_high*100:.1f}%")
    print(f"P(Local | Q_t = 0)  = {p_local_zero*100:.1f}%")

def run_ablation(env, base_agent, num_episodes=20):
    print("\n--- Observation Ablation Analysis ---")
    
    conditions = {
        "Unmasked (Baseline)": MaskedAgent(base_agent, False, False),
        "Mask Q_t": MaskedAgent(base_agent, True, False),
        "Mask T_queue": MaskedAgent(base_agent, False, True),
        "Mask Both": MaskedAgent(base_agent, True, True)
    }
    
    for name, agent in conditions.items():
        success = []
        reward = []
        for ep in range(num_episodes):
            obs = env.reset(seed=200 + ep)
            dones = {"__all__": False}
            
            while not dones["__all__"]:
                actions = {}
                for i in range(env.n_vehicles):
                    is_safety = (obs[i][11] == 1.0)
                    actions[i] = agent.select_action(obs[i], is_safety_task=is_safety, evaluate=True)
                
                obs, rewards, dones, infos = env.step(actions)
                
                for i in range(env.n_vehicles):
                    if infos[i]["has_task"]:
                        success.append(infos[i]["S_i"])
                        reward.append(rewards[i])
        
        print(f"{name:>20} -> Success: {np.mean(success)*100:5.1f}% | Reward: {np.mean(reward):.3f}")

if __name__ == "__main__":
    agent = D3QNAgent(state_dim=20, action_dim=11, seed=42)
    agent.load("checkpoints_shared/best.pt")
    agent.epsilon = 0.0
    
    print("========== SCENARIO B (Moderate Load) ==========")
    env_b = V2XEnvPlus(n_vehicles=16, seed=42, f_mec=0.316e9, bg_workload_enabled=True)
    run_queue_analysis(env_b, agent, num_episodes=30)
    run_ablation(env_b, agent, num_episodes=30)
    
    print("\n========== SCENARIO C (Heavy Load) ==========")
    env_c = V2XEnvPlus(n_vehicles=16, seed=42, f_mec=0.250e9, bg_workload_enabled=True)
    run_queue_analysis(env_c, agent, num_episodes=30)
    run_ablation(env_c, agent, num_episodes=30)
