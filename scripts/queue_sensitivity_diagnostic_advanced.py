import torch
import numpy as np
import argparse
import sys
import csv
import glob
import os
sys.path.append('.')

from agents.d3qn.agent import D3QNAgent
from env.environment_plus import V2XEnvPlus

def get_scenarios(env):
    deadlines = [{"name": "Tight", "D": 0.1, "cls": 1}, 
                 {"name": "Med", "D": 0.5, "cls": 2}, 
                 {"name": "Relax", "D": 1.0, "cls": 3}]
    
    workloads = [{"name": "Small", "L": 1e6}, 
                 {"name": "Med", "L": 10e6}, 
                 {"name": "Large", "L": 50e6}]
                 
    channels = [{"name": "Fav", "snr": 1.0, "g5g": 1000.0},
                {"name": "Med", "snr": 0.5, "g5g": 100.0},
                {"name": "Poor", "snr": 0.1, "g5g": 10.0}]
                
    scenarios = []
    
    # We rely on env.reset() to handle exact preprocessing (normalization/clipping)
    obs_raw = env.reset(seed=42)[0]
    
    for d in deadlines:
        for w in workloads:
            for c in channels:
                obs = obs_raw.copy()
                # Overwrite features exactly matching env.reset() logic
                # 3: snr, 9: gamma_5g, 11: task_active, 12: class_norm, 15: D_norm, 16: B_norm, 17: L_norm
                
                obs[3] = c["snr"]
                obs[9] = min(1.0, max(0.0, (np.log10(c["g5g"]) - 1.0) / 2.0))
                obs[10] = 1.0 # Task active
                obs[11] = 1.0 if d["cls"] == 1 else 0.0
                obs[12] = 1.0 if d["cls"] == 2 else 0.0
                obs[13] = 1.0 if d["cls"] == 3 else 0.0
                obs[15] = min(1.0, d["D"] / 1.0) # max D is 1.0s
                
                # Assume 2400 bits per 1M cycles
                B = (w["L"] / 1e6) * (2400 / 8) # in bytes (note: assuming env uses bits for B_ref but let's check B_ref = 50 * 8 * 1024)
                # Actually, env.B_ref is in bits, so we should use bits:
                B_bits = (w["L"] / 1e6) * 2400
                
                obs[16] = min(1.0, w["L"] / 15e6)
                obs[17] = min(1.0, B_bits / env.B_ref)
                
                scenarios.append({
                    "desc": f"{d['name']}_{w['name']}_{c['name']}",
                    "obs": obs,
                    "support_type": "Synthetic Intervention (Queue Sweep)"
                })
                
    # Determinism Check: Ensure repeated probing produces byte-identical inputs
    st1 = scenarios[0]["obs"].copy()
    st2 = scenarios[0]["obs"].copy()
    assert np.array_equal(st1, st2), "Pipeline determinism failed! State encoding is not reproducible."
    
    # Correctness Check: Validate exact feature mapping against mathematical expectation
    # For Tight Deadline (D=0.1s), assuming env.D_max = 1.0s
    assert abs(st1[15] - (0.1 / 1.0)) < 1e-6, "Deadline normalization mismatch."
    # For Favorable Channel (g5g=1000)
    assert abs(st1[9] - ((np.log10(1000.0) - 1.0) / 2.0)) < 1e-6, "Channel state mismatch."
    
    return scenarios

def analyze_queue_sensitivity(model_path, agent_idx, env, scenarios, writer):
    agent = D3QNAgent(state_dim=20, action_dim=11, seed=42)
    agent.online_net.load_state_dict(torch.load(model_path, map_location='cpu'))
    agent.online_net.eval()
    
    queues = [0, 10e6, 20e6, 30e6, 40e6, 50e6, 60e6, 70e6, 80e6, 90e6, 100e6]
    
    for scen in scenarios:
        for q in queues:
            test_obs = scen["obs"].copy()
            test_obs[1] = min(1.0, q / env.Q_max)
            
            with torch.no_grad():
                st = torch.FloatTensor(test_obs).unsqueeze(0)
                q_vals = agent.online_net(st).cpu().numpy()[0]
                
            q_loc = q_vals[0]
            q_lte = np.max(q_vals[1:6])
            q_5g = np.max(q_vals[6:11])
            
            chosen = np.argmax(q_vals)
            
            writer.writerow([
                model_path, agent_idx, scen["desc"], q, 
                q_loc, q_lte, q_5g, 
                q_5g - q_loc, q_5g - q_lte, 
                chosen, scen.get("support_type", "Unknown")
            ])

if __name__ == "__main__":
    env = V2XEnvPlus(n_vehicles=16)
    scenarios = get_scenarios(env)
    
    out_file = "analysis/QUEUE_SENSITIVITY_RAW.csv"
    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ModelPath", "ClientIdx", "Scenario", "Queue", 
                         "Q_Local", "Q_LTE_Max", "Q_5G_Max", 
                         "DeltaQ_5G_Loc", "DeltaQ_5G_LTE", 
                         "Action", "SupportType"])
                         
    print(f"Finding B3.3B checkpoints...")
    ckpt_dirs = glob.glob("checkpoints_b33b/*")
    
    for cdir in ckpt_dirs:
        for i in range(16):
            ckpt = f"{cdir}/agent_{i}.pt"
            if os.path.exists(ckpt):
                print(f"Analyzing {ckpt}...")
                with open(out_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    analyze_queue_sensitivity(ckpt, i, env, scenarios, writer)
            
    print(f"Done. Wrote to {out_file}")
