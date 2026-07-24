import os
import json
import datetime
import torch
import math
import numpy as np
from env.environment import V2XEnv
from agents.d3qn.agent import D3QNAgent
from agents.federated.coordinator_plus import FederatedCoordinatorPlus

def evaluate_policy(env, agents, n_vehicles, seed):
    for i in range(n_vehicles):
        agents[i].epsilon = 0.0
        agents[i].online_net.eval()
        
    env.policy_type = "learned"
    
    eval_metrics = {
        "u_prr": [], "u_otr": [], "otr": [], "prr": [],
        "actions": []
    }
    
    # Run 5 episodes of evaluation
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
                
                u_otr = (0.3 * otr_val + 0.4 * math.exp(-l_ratio) + 0.3 * math.exp(-e_ratio))
                eval_metrics["u_otr"].append(np.clip(u_otr, 0.0, 1.0))
            
            obs = next_obs
            
    for i in range(n_vehicles):
        agents[i].online_net.train()
        
    return {
        "u_prr": float(np.mean(eval_metrics["u_prr"])),
        "u_otr": float(np.mean(eval_metrics["u_otr"])),
        "fleet_otr": float(np.mean(eval_metrics["otr"])),
        "action_dist": {k: eval_metrics["actions"].count(k)/len(eval_metrics["actions"]) for k in set(eval_metrics["actions"])}
    }

def main():
    seed = 0
    n_vehicles = 8
    mode = "ma_rope"
    profile = "marope_compute_calibrated_mb"
    episodes = 200
    eval_interval = 20
    
    os.makedirs("results/marope_calibrated_mb_validation", exist_ok=True)
    
    env = V2XEnv(n_vehicles=n_vehicles, seed=seed, physics_mode=mode)
    env.calibration_profile = profile
    
    agents = {i: D3QNAgent(state_dim=12, action_dim=11, seed=seed+i) for i in range(n_vehicles)}
    coord = FederatedCoordinatorPlus(n_agents=n_vehicles)
    
    history = []
    
    for ep in range(1, episodes + 1):
        obs = env.reset(seed=seed + ep)
        dones = {"__all__": False}
        infos_history = []
        ep_rewards = []
        
        while not dones["__all__"]:
            actions = {}
            for i in range(n_vehicles):
                is_safety = (env.active_tasks[i]["type"] == "safety")
                actions[i] = agents[i].select_action(obs[i], is_safety_task=is_safety)
            
            next_obs, rewards, dones, infos = env.step(actions)
            infos_history.append(infos)
            ep_rewards.append(list(rewards.values()))
            
            for i in range(n_vehicles):
                agents[i].replay_buffer.add(obs[i], actions[i], rewards[i], next_obs[i], dones["__all__"])
                agents[i].learn()
            
            obs = next_obs
            
        if ep % 10 == 0:
            agent_models = {i: agents[i].online_net.state_dict() for i in range(n_vehicles)}
            global_state, report = coord.aggregate_and_broadcast(agent_models, infos_history[-1])
            if report["round_executed"]:
                for i in range(n_vehicles):
                    agents[i].online_net.load_state_dict(global_state)
                    lr = agents[i].optimizer.param_groups[0]['lr']
                    agents[i].optimizer = torch.optim.Adam(agents[i].online_net.parameters(), lr=lr)
                    agents[i].update_target_network()
                    
        if ep % eval_interval == 0:
            eval_res = evaluate_policy(env, agents, n_vehicles, seed)
            record = {
                "episode": ep,
                "train_reward_avg": float(np.mean(ep_rewards)),
                "epsilon": agents[0].epsilon,
                "eval": eval_res
            }
            print(f"Ep {ep:3d} | Eps {agents[0].epsilon:.3f} | Eval U_PRR {eval_res['u_prr']:.4f} | Local Actions {eval_res['action_dist'].get(0, 0.0):.1%}")
            history.append(record)
            
    with open("results/marope_calibrated_mb_validation/training_history.json", "w") as f:
        json.dump(history, f, indent=4)
    print("Training finished.")

if __name__ == "__main__":
    main()
