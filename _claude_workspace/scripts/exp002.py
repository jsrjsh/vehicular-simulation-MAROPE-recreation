import os
import json
import torch
import math
import numpy as np
import copy
from env.environment import V2XEnv
from agents.d3qn.agent import D3QNAgent
from agents.federated.coordinator_plus import FederatedCoordinatorPlus
import time

def evaluate_policy(env, agents, n_vehicles, seed):
    for i in range(n_vehicles):
        agents[i].epsilon = 0.0
        agents[i].online_net.eval()
        
    env.policy_type = "learned"
    
    eval_metrics = {
        "u_prr": [], "latency": [], "energy": [], "otr": [], "prr": [],
        "actions": [], "rhos": [], "adapted_rhos": []
    }
    
    for ep in range(1, 6):
        obs = env.reset(seed=seed + 1000 + ep)
        dones = {"__all__": False}
        
        while not dones["__all__"]:
            actions = {}
            for i in range(n_vehicles):
                is_safety = (env.active_tasks[i]["type"] == "safety")
                actions[i] = agents[i].select_action(obs[i], is_safety_task=is_safety, evaluate=True)
                
            next_obs, rewards, dones, infos = env.step(actions)
            
            for i in range(n_vehicles):
                eval_metrics["prr"].append(infos[i]["empirical_prr"])
                eval_metrics["actions"].append(infos[i]["chosen_rat"])
                eval_metrics["rhos"].append(infos[i]["chosen_rho"])
                if "adapted_rho" in infos[i]:
                    eval_metrics["adapted_rhos"].append(infos[i]["adapted_rho"])
                
                eval_metrics["latency"].append(infos[i]["latency_ms"])
                eval_metrics["energy"].append(infos[i]["energy_j"])
                
                task = env.active_tasks[i]
                l_ratio = max(min(infos[i]["latency_ms"] / task["D_ms"], 100.0), -100.0)
                e_ratio = max(min(infos[i]["energy_j"] / 3.0, 100.0), -100.0)
                
                u_prr = (0.3 * infos[i]["empirical_prr"] + 0.4 * math.exp(-l_ratio) + 0.3 * math.exp(-e_ratio))
                eval_metrics["u_prr"].append(np.clip(u_prr, 0.0, 1.0))
                
                rat_idx = infos[i]["chosen_rat"]
                if rat_idx == 0 or infos[i]["chosen_rho"] == 0.0:
                    otr_val = 1.0
                else:
                    otr_val = 1.0 if infos[i]["latency_ms"] <= task["D_ms"] else 0.0
                eval_metrics["otr"].append(otr_val)
            
            obs = next_obs
            
    for i in range(n_vehicles):
        agents[i].online_net.train()
        
    return {
        "u_prr": float(np.mean(eval_metrics["u_prr"])),
        "latency": float(np.mean(eval_metrics["latency"])),
        "energy": float(np.mean(eval_metrics["energy"])),
        "prr": float(np.mean(eval_metrics["prr"])),
        "otr": float(np.mean(eval_metrics["otr"])),
        "action_dist": {str(k): eval_metrics["actions"].count(k)/len(eval_metrics["actions"]) for k in set(eval_metrics["actions"])},
    }

def run_experiment(name, sync_freq):
    seeds = [0, 1, 2] # 3 seeds
    n_vehicles = 8
    episodes = 100
    
    results = {}
        
    for seed in seeds:
        print(f"Running {name} - Seed {seed}")
        env = V2XEnv(n_vehicles=n_vehicles, seed=seed, mode="physically_corrected")
        env.calibration_profile = "marope_compute_calibrated_mb"
        
        agents = {i: D3QNAgent(state_dim=12, action_dim=11, seed=seed+i) for i in range(n_vehicles)}
        coord = FederatedCoordinatorPlus(n_agents=n_vehicles)
        
        seed_hist = []
        # Evaluate at start
        eval_res = evaluate_policy(env, agents, n_vehicles, seed)
        seed_hist.append({"ep": 0, "eval": eval_res})
        
        for ep in range(1, episodes + 1):
            obs = env.reset(seed=seed + ep)
            dones = {"__all__": False}
            infos_history = []
            
            while not dones["__all__"]:
                actions_dict = {}
                for i in range(n_vehicles):
                    is_safety = (env.active_tasks[i]["type"] == "safety")
                    actions_dict[i] = agents[i].select_action(obs[i], is_safety_task=is_safety)
                
                next_obs, rewards, dones, infos = env.step(actions_dict)
                infos_history.append(infos)
                
                for i in range(n_vehicles):
                    agents[i].replay_buffer.add(obs[i], actions_dict[i], rewards[i], next_obs[i], dones["__all__"])
                    agents[i].learn()
                
                obs = next_obs
                
            if ep % sync_freq == 0:
                agent_models = {i: agents[i].online_net.state_dict() for i in range(n_vehicles)}
                global_state, report = coord.aggregate_and_broadcast(agent_models, infos_history[-1])
                if report["round_executed"]:
                    for i in range(n_vehicles):
                        agents[i].online_net.load_state_dict(global_state)
                        lr = agents[i].optimizer.param_groups[0]['lr']
                        agents[i].optimizer = torch.optim.Adam(agents[i].online_net.parameters(), lr=lr)
                        agents[i].update_target_network()
                        
            if ep % 20 == 0:
                eval_res = evaluate_policy(env, agents, n_vehicles, seed)
                seed_hist.append({"ep": ep, "eval": eval_res})
                print(f"  Ep {ep} | U={eval_res['u_prr']:.3f} | Local={eval_res['action_dist'].get('0', 0.0):.1%}")
        results[seed] = seed_hist
        
    return results

if __name__ == "__main__":
    os.makedirs("results/exp002", exist_ok=True)
    
    print("--- RUNNING CONTROL (Sync=10) ---")
    res_control = run_experiment("control", sync_freq=10)
    with open("results/exp002/control.json", "w") as f:
        json.dump(res_control, f, indent=2)
        
    print("\n--- RUNNING CANDIDATE (Sync=1) ---")
    res_candidate = run_experiment("candidate", sync_freq=1)
    with open("results/exp002/candidate.json", "w") as f:
        json.dump(res_candidate, f, indent=2)
    
    print("Experiments completed.")
