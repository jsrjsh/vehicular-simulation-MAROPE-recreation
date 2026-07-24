import torch
import numpy as np
import argparse
import sys
sys.path.append('.')

from agents.d3qn.agent import D3QNAgent
from env.environment_plus import V2XEnvPlus

def analyze_queue_sensitivity(model_path, seed=42):
    env = V2XEnvPlus(n_vehicles=16, seed=seed)
    
    agent = D3QNAgent(state_dim=20, action_dim=11, seed=seed)
    agent.online_net.load_state_dict(torch.load(model_path))
    agent.online_net.eval()
    
    # Fix environment state
    obs = env.reset(seed=seed)
    
    # We will manipulate vehicle 0's observation
    base_obs = obs[0].copy()
    
    # Ensure active task exists (Class 1, Tight Deadline)
    base_obs[11] = 1.0 # Task active flag
    base_obs[12] = 0.5 # Normalized Class 1
    base_obs[15] = 0.1 # Very tight deadline (100ms)
    base_obs[16] = 2000.0 / env.B_ref # Small task size
    base_obs[17] = 0.5e6 / env.L_ref # CPU cycles needed
    
    # Excellent channel conditions to eliminate offload failure risk
    base_obs[3] = 1.0 # High SNR
    base_obs[9] = 1.0 # High Gamma 5G
    
    queues_to_test = [0, 10e6, 20e6, 30e6, 40e6, 50e6, 60e6, 70e6, 80e6, 90e6, 100e6]
    
    results = []
    
    print(f"--- Queue Sensitivity Analysis ---")
    print(f"Model: {model_path}")
    print(f"{'Queue (M cycles)':<15} | {'Q(Local)':<10} | {'Q(LTE)':<10} | {'Q(5G)':<10} | {'Action'}")
    print("-" * 65)
    
    for q in queues_to_test:
        test_obs = base_obs.copy()
        test_obs[1] = q / env.Q_max
        
        state_tensor = torch.FloatTensor(test_obs).unsqueeze(0).to(agent.device)
        with torch.no_grad():
            q_values = agent.online_net(state_tensor).cpu().numpy()[0]
            
        q_local = q_values[0]
        q_lte = np.mean(q_values[1:6]) # Avg LTE channels
        q_5g = np.mean(q_values[6:11]) # Avg 5G channels
        
        action = np.argmax(q_values)
        if action == 0:
            act_str = "Local"
        elif 1 <= action <= 5:
            act_str = "LTE"
        else:
            act_str = "5G"
            
        print(f"{q/1e6:>13.1f} | {q_local:>10.3f} | {q_lte:>10.3f} | {q_5g:>10.3f} | {act_str}")
        
        results.append({
            "queue": q,
            "q_local": q_local,
            "q_lte": q_lte,
            "q_5g": q_5g,
            "action": act_str
        })
        
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, help="Path to .pt model file")
    args = parser.parse_args()
    analyze_queue_sensitivity(args.model)
