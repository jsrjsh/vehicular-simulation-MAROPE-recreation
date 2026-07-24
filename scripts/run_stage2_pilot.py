import os
import csv
import numpy as np
import torch
import torch.optim as optim

import sys
sys.path.append('.')

from env.environment_plus import V2XEnvPlus
from agents.d3qn.agent import D3QNAgent
from agents.federated.coordinator_plus import FederatedCoordinatorPlus
from scripts.train_b3_baselines import Evaluator

def run_pilot(agent_mode, config_name, w_s, w_t, w_e, reward_type, seed, episodes=200):
    env = V2XEnvPlus(n_vehicles=16, seed=seed, f_mec=0.316e9, bg_workload_enabled=True,
                     w_s=w_s, w_t=w_t, w_e=w_e, reward_type=reward_type)
    evaluator = Evaluator(env)
    
    agents = {i: D3QNAgent(state_dim=20, action_dim=11, seed=seed + i) for i in range(16)}
    coord = FederatedCoordinatorPlus(n_agents=16, theta_round=0.7)
    
    final_metrics = None
    
    for episode in range(1, episodes + 1):
        obs = env.reset(seed=seed + episode)
        dones = {"__all__": False}
        
        while not dones["__all__"]:
            actions = {}
            for i in range(16):
                is_safety = (obs[i][11] == 1.0)
                actions[i] = agents[i].select_action(obs[i], is_safety_task=is_safety)
                
            next_obs, rewards, dones, infos = env.step(actions)
            
            for i in range(16):
                if infos[i]["has_task"]:
                    agents[i].replay_buffer.add(obs[i], infos[i]["effective_action"], rewards[i], next_obs[i], dones["__all__"])
                    agents[i].learn()
                    
            obs = next_obs
            
        if agent_mode == "fedavg" and episode % 10 == 0:
            agent_models = {i: agents[i].online_net.state_dict() for i in range(16)}
            global_state, report = coord.aggregate_and_broadcast(agent_models, infos)
            if report["round_executed"]:
                for i in range(16):
                    agents[i].online_net.load_state_dict(global_state)
                    lr = agents[i].optimizer.param_groups[0]['lr']
                    agents[i].optimizer = optim.Adam(agents[i].online_net.parameters(), lr=lr)
                    agents[i].update_target_network()
                    
        if episode == episodes:
            final_metrics = evaluator.evaluate(agents, agent_mode, num_eps=10) # 10 eps eval at end
            
            # Save checkpoints
            os.makedirs(f"checkpoints_b33b/{agent_mode}_{config_name}_seed_{seed}", exist_ok=True)
            for i in range(16):
                agents[i].save(f"checkpoints_b33b/{agent_mode}_{config_name}_seed_{seed}/agent_{i}.pt")
            
    return final_metrics

if __name__ == "__main__":
    configs = [
        {"name": "Baseline", "w_s": 0.4, "w_t": 0.3, "w_e": 0.2, "reward_type": "linear"},
        {"name": "Candidate_B", "w_s": 0.0, "w_t": 0.0, "w_e": 0.0, "reward_type": "piecewise"},
        {"name": "Candidate_C", "w_s": 0.4, "w_t": 0.3, "w_e": 0.2, "reward_type": "sigmoid"}
    ]
    
    modes = ["independent", "fedavg"]
    
    seeds = [111, 222, 333]
    
    os.makedirs("analysis", exist_ok=True)
    out_file = "analysis/stage2_pilot_results.csv"
    
    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Mode", "Config", "Seed", "RewardType", "5G_Ratio", "SLA_Success", "Energy", "Latency_ms"])
        
    for mode in modes:
        for cfg in configs:
            for seed in seeds:
                print(f"Running {mode.upper()} - {cfg['name']} (Seed {seed})...")
                metrics = run_pilot(mode, cfg["name"], cfg["w_s"], cfg["w_t"], cfg["w_e"], cfg["reward_type"], seed)
                
                ratio_5g = metrics["action_dist"].get(2, 0.0)
                success = metrics["success_rate"]
                energy = metrics["energy"]
                latency = metrics["latency_all"] * 1000 # to ms
                
                with open(out_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([mode, cfg["name"], seed, cfg["reward_type"], ratio_5g, success, energy, latency])
                
                print(f"  -> 5G Ratio: {ratio_5g*100:.1f}% | SLA: {success*100:.1f}% | E: {energy:.2f}mJ")
            
    print(f"Sweep complete! Results saved to {out_file}")
