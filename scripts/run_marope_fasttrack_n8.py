import os
import json
import csv
import math
import numpy as np
import datetime
import torch
from env.environment import V2XEnv
from agents.d3qn.agent import D3QNAgent
from agents.federated.coordinator_plus import FederatedCoordinatorPlus

def run_experiment(seed=0, n_vehicles=8, mode="ma_rope", policy_type="learned"):
    print(f"Running Seed {seed} | Policy {policy_type} | Mode {mode}")
    env = V2XEnv(n_vehicles=n_vehicles, seed=seed, physics_mode=mode)
    
    agents = {i: D3QNAgent(state_dim=12, action_dim=11, seed=seed+i) for i in range(n_vehicles)}
    if policy_type == "learned":
        coord = FederatedCoordinatorPlus(n_agents=n_vehicles)
        
        # Training (100 episodes)
        for ep in range(1, 101):
            obs = env.reset()
            dones = {"__all__": False}
            infos_history = []
            
            while not dones["__all__"]:
                actions = {}
                for i in range(n_vehicles):
                    is_safety = (env.active_tasks[i]["type"] == "safety")
                    actions[i] = agents[i].select_action(obs[i], is_safety_task=is_safety)
                
                next_obs, rewards, dones, infos = env.step(actions)
                infos_history.append(infos)
                
                for i in range(n_vehicles):
                    agents[i].replay_buffer.add(obs[i], actions[i], rewards[i], next_obs[i], dones["__all__"])
                    agents[i].learn()
                
                obs = next_obs
            
            # FedAvg every 10 episodes
            if ep % 10 == 0:
                agent_models = {i: agents[i].online_net.state_dict() for i in range(n_vehicles)}
                global_state, report = coord.aggregate_and_broadcast(agent_models, infos_history[-1])
                if report["round_executed"]:
                    for i in range(n_vehicles):
                        agents[i].online_net.load_state_dict(global_state)
                        lr = agents[i].optimizer.param_groups[0]['lr']
                        agents[i].optimizer = torch.optim.Adam(agents[i].online_net.parameters(), lr=lr)
                        agents[i].update_target_network()

    # Evaluation (5 episodes, frozen)
    eval_metrics = {
        "u_prr": [], "u_otr": [], "otr": [], "prr": [],
        "latency": [], "energy": [], "queue": [], "actions": []
    }
    
    for i in range(n_vehicles):
        agents[i].epsilon = 0.0 # fully greedy
        agents[i].online_net.eval()
        
    env.policy_type = policy_type 
    
    for ep in range(1, 6):
        obs = env.reset(seed=seed + 1000 + ep)
        dones = {"__all__": False}
        
        while not dones["__all__"]:
            actions = {}
            for i in range(n_vehicles):
                if policy_type == "learned":
                    is_safety = (env.active_tasks[i]["type"] == "safety")
                    actions[i] = agents[i].select_action(obs[i], is_safety_task=is_safety, evaluate=True)
                elif policy_type == "alloffload":
                    actions[i] = 8 # 5G 100%
                elif policy_type == "nooffload":
                    actions[i] = 0 # Local
                else:
                    actions[i] = 0
                    
            next_obs, rewards, dones, infos = env.step(actions)
            
            for i in range(n_vehicles):
                eval_metrics["latency"].append(infos[i]["latency_ms"])
                eval_metrics["energy"].append(infos[i]["energy_j"])
                eval_metrics["prr"].append(infos[i]["empirical_prr"])
                eval_metrics["queue"].append(infos[i].get("queue_delay_ms", 0.0))
                eval_metrics["actions"].append(infos[i]["chosen_rat"])
                
                task = env.active_tasks[i]
                l_ratio = max(min(infos[i]["latency_ms"] / task["D_ms"], 100.0), -100.0)
                e_ratio = max(min(infos[i]["energy_j"] / 3.0, 100.0), -100.0)
                
                u_prr = (0.3 * infos[i]["empirical_prr"]
                         + 0.4 * math.exp(-l_ratio)
                         + 0.3 * math.exp(-e_ratio))
                eval_metrics["u_prr"].append(np.clip(u_prr, 0.0, 1.0))
                
                rat_idx = infos[i]["chosen_rat"]
                if rat_idx == 0 or infos[i]["chosen_rho"] == 0.0:
                    otr_val = 1.0
                else:
                    otr_val = 1.0 if infos[i]["latency_ms"] <= task["D_ms"] else 0.0
                
                eval_metrics["otr"].append(otr_val)
                
                u_otr = (0.3 * otr_val
                         + 0.4 * math.exp(-l_ratio)
                         + 0.3 * math.exp(-e_ratio))
                eval_metrics["u_otr"].append(np.clip(u_otr, 0.0, 1.0))
            
            obs = next_obs
            
    res = {
        "u_prr": float(np.mean(eval_metrics["u_prr"])),
        "u_otr": float(np.mean(eval_metrics["u_otr"])),
        "fleet_otr": float(np.mean(eval_metrics["otr"])),
        "latency_ms": float(np.mean(eval_metrics["latency"])),
        "energy_j": float(np.mean(eval_metrics["energy"])),
        "prr": float(np.mean(eval_metrics["prr"])),
        "queue_ms": float(np.mean(eval_metrics["queue"])),
        "action_dist": {k: eval_metrics["actions"].count(k)/len(eval_metrics["actions"]) for k in set(eval_metrics["actions"])}
    }
    
    ckpt_path = None
    if policy_type == "learned":
        os.makedirs(f"results/marope_fasttrack_n8/checkpoints/{mode}_seed{seed}", exist_ok=True)
        for i in range(n_vehicles):
            torch.save(agents[i].online_net.state_dict(), f"results/marope_fasttrack_n8/checkpoints/{mode}_seed{seed}/agent_{i}.pt")
        ckpt_path = f"results/marope_fasttrack_n8/checkpoints/{mode}_seed{seed}/"
        
    return res, ckpt_path

def main():
    os.makedirs("results/marope_fasttrack_n8", exist_ok=True)
    seeds = [0, 1, 2, 3, 4]
    policies = ["learned", "alloffload", "nooffload"]
    
    results = {}
    
    for policy in policies:
        results[policy] = []
        for seed in seeds:
            res, ckpt = run_experiment(seed=seed, n_vehicles=8, mode="ma_rope", policy_type=policy)
            record = {
                "timestamp": str(datetime.datetime.now()),
                "seed": seed,
                "physics_mode": "ma_rope",
                "policy": policy,
                "metrics": res,
                "checkpoint": ckpt
            }
            results[policy].append(record)
            
            with open(f"results/marope_fasttrack_n8/raw_{policy}_seed{seed}.json", "w") as f:
                json.dump(record, f, indent=4)
                
    agg = {}
    for policy in policies:
        u_prr = [r["metrics"]["u_prr"] for r in results[policy]]
        u_otr = [r["metrics"]["u_otr"] for r in results[policy]]
        fleet_otr = [r["metrics"]["fleet_otr"] for r in results[policy]]
        agg[policy] = {
            "u_prr_mean": float(np.mean(u_prr)),
            "u_prr_std": float(np.std(u_prr)),
            "u_otr_mean": float(np.mean(u_otr)),
            "u_otr_std": float(np.std(u_otr)),
            "fleet_otr_mean": float(np.mean(fleet_otr)),
            "fleet_otr_std": float(np.std(fleet_otr))
        }
        
    with open("results/marope_fasttrack_n8/aggregate.json", "w") as f:
        json.dump(agg, f, indent=4)
        
    print("DONE. Results saved in results/marope_fasttrack_n8/")

if __name__ == "__main__":
    main()
