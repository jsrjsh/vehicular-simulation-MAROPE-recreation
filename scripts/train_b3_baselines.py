import argparse
import copy
import json
import os
import csv
import numpy as np
import torch
import torch.optim as optim
from collections import deque
from env.environment_plus import V2XEnvPlus
from agents.d3qn.agent import D3QNAgent
from agents.federated.coordinator_plus import FederatedCoordinatorPlus

def get_args():
    parser = argparse.ArgumentParser(description="MA-ROPE+ Phase B3 Baselines")
    parser.add_argument("--mode", type=str, choices=["shared", "independent", "fedavg", "random", "heuristic"], required=True)
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--n_vehicles", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--eval_interval", type=int, default=20)
    parser.add_argument("--eval_eps", type=int, default=5)
    return parser.parse_args()

class Evaluator:
    def __init__(self, env):
        self.env = env
        
    def evaluate(self, agents, mode, num_eps=5):
        is_shared = (mode == "shared")
        global_agent = agents[0] if is_shared else None
        
        metrics = {
            "success_rate": [],
            "latency_all": [],
            "latency_success": [],
            "energy": [],
            "queue": [],
            "action_dist": {0:0, 1:0, 2:0} # Local, LTE, 5G
        }
        
        client_metrics = {i: {"success_rate": [], "reward": []} for i in range(self.env.n_vehicles)}
        
        for ep in range(num_eps):
            obs = self.env.reset(seed=42 + ep*100) # Deterministic eval seeds
            dones = {"__all__": False}
            
            while not dones["__all__"]:
                actions = {}
                for i in range(self.env.n_vehicles):
                    if mode == "random":
                        is_safety = (obs[i][11] == 1.0)
                        if is_safety:
                            a = np.random.choice([0, 4, 5, 6, 7, 8, 9, 10])
                        else:
                            a = np.random.choice(11)
                    elif mode == "heuristic":
                        # D < 0.2 -> Local (0), else -> 5G full offload (10)
                        a = 0 if obs[i][15] < 0.2 else 10
                    else:
                        agent = global_agent if is_shared else agents[i]
                        is_safety = (obs[i][11] == 1.0)
                        a = agent.select_action(obs[i], is_safety_task=is_safety, evaluate=True)
                    actions[i] = a
                
                obs, rewards, dones, infos = self.env.step(actions)
                
                for i in range(self.env.n_vehicles):
                    if infos[i]["has_task"]:
                        S_i = infos[i]["S_i"]
                        T_i = infos[i]["T_i"]
                        E_i = infos[i]["E_i"]
                        Q_t = obs[i][1] * self.env.Q_max
                        
                        metrics["success_rate"].append(S_i)
                        metrics["energy"].append(E_i)
                        metrics["queue"].append(Q_t)
                        metrics["latency_all"].append(T_i)
                        if S_i == 1.0:
                            metrics["latency_success"].append(T_i)
                            
                        client_metrics[i]["success_rate"].append(S_i)
                        client_metrics[i]["reward"].append(rewards[i])
                            
                        # Action dist
                        eff_act = infos[i]["effective_action"]
                        if eff_act == 0:
                            metrics["action_dist"][0] += 1
                        elif 1 <= eff_act <= 5:
                            metrics["action_dist"][1] += 1
                        else:
                            metrics["action_dist"][2] += 1
                            
        # Aggregate
        total_actions = sum(metrics["action_dist"].values())
        if total_actions > 0:
            act_dist = {k: v/total_actions for k,v in metrics["action_dist"].items()}
        else:
            act_dist = metrics["action_dist"]
            
        # Per-client stats
        client_successes = []
        client_rewards = []
        for i in range(self.env.n_vehicles):
            s_i = np.mean(client_metrics[i]["success_rate"]) if client_metrics[i]["success_rate"] else 0.0
            r_i = np.mean(client_metrics[i]["reward"]) if client_metrics[i]["reward"] else 0.0
            client_successes.append(s_i)
            client_rewards.append(r_i)
            
        return {
            "success_rate": np.mean(metrics["success_rate"]) if metrics["success_rate"] else 0.0,
            "latency_all": np.mean(metrics["latency_all"]) if metrics["latency_all"] else 0.0,
            "latency_success": np.mean(metrics["latency_success"]) if metrics["latency_success"] else 0.0,
            "energy": np.mean(metrics["energy"]) if metrics["energy"] else 0.0,
            "queue": np.mean(metrics["queue"]) if metrics["queue"] else 0.0,
            "action_dist": act_dist,
            "success_disp": np.std(client_successes) if client_successes else 0.0,
            "reward_disp": np.std(client_rewards) if client_rewards else 0.0
        }

def train():
    args = get_args()
    print(f"--- Starting {args.mode.upper()} Baseline ---")
    
    # Setup Checkpoint & Logging Dirs
    os.makedirs(f"checkpoints_{args.mode}", exist_ok=True)
    csv_file = f"results_{args.mode}_seed_{args.seed}.csv"
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["episode", "reward", "success_rate", "latency_success", "latency_all", 
                         "energy", "queue", "epsilon", "td_loss", "avg_q", 
                         "aggregation_round", "eligible_fraction", "uplink_bytes", "downlink_bytes",
                         "div_before", "div_after", "success_disp", "reward_disp"])
    
    env = V2XEnvPlus(n_vehicles=args.n_vehicles, seed=args.seed, f_mec=0.316e9, bg_workload_enabled=True)
    evaluator = Evaluator(env)
    
    # Initialize agents
    if args.mode in ["shared"]:
        agents = {0: D3QNAgent(state_dim=20, action_dim=11, seed=args.seed)}
    elif args.mode in ["independent", "fedavg"]:
        agents = {i: D3QNAgent(state_dim=20, action_dim=11, seed=args.seed + i) for i in range(args.n_vehicles)}
    else:
        agents = {}
        
    coord = FederatedCoordinatorPlus(n_agents=args.n_vehicles, theta_round=0.7) if args.mode == "fedavg" else None
    
    best_success = -1.0
    
    for episode in range(1, args.episodes + 1):
        obs = env.reset(seed=args.seed + episode)
        dones = {"__all__": False}
        ep_reward = 0
        ep_losses = []
        ep_qs = []
        
        while not dones["__all__"]:
            actions = {}
            for i in range(args.n_vehicles):
                if args.mode == "random":
                    is_safety = (obs[i][11] == 1.0)
                    if is_safety:
                        a = np.random.choice([0, 4, 5, 6, 7, 8, 9, 10])
                    else:
                        a = np.random.choice(11)
                elif args.mode == "heuristic":
                    a = 0 if obs[i][15] < 0.2 else 10
                else:
                    agent = agents[0] if args.mode == "shared" else agents[i]
                    is_safety = (obs[i][11] == 1.0)
                    a = agent.select_action(obs[i], is_safety_task=is_safety)
                actions[i] = a
                
            next_obs, rewards, dones, infos = env.step(actions)
            
            for i in range(args.n_vehicles):
                # Only active tasks stored in replay buffer
                if infos[i]["has_task"]:
                    ep_reward += rewards[i]
                    if args.mode not in ["random", "heuristic"]:
                        agent = agents[0] if args.mode == "shared" else agents[i]
                        agent.replay_buffer.add(obs[i], infos[i]["effective_action"], rewards[i], next_obs[i], dones["__all__"])
                        loss, q_val = agent.learn() # 1 update per env step
                        if loss > 0.0:
                            ep_losses.append(loss)
                            ep_qs.append(q_val)
                    
            obs = next_obs
            
        avg_td_loss = np.mean(ep_losses) if ep_losses else 0.0
        avg_q_val = np.mean(ep_qs) if ep_qs else 0.0
        current_eps = agents[0].epsilon if args.mode in ["shared", "independent", "fedavg"] else 0.0
            
        agg_round = 0
        el_frac = 0.0
        up_bytes = 0
        dn_bytes = 0
        
        # End of episode FedAvg aggregation
        if args.mode == "fedavg" and episode % 10 == 0:
            agent_models = {i: agents[i].online_net.state_dict() for i in range(args.n_vehicles)}
            global_state, report = coord.aggregate_and_broadcast(agent_models, infos)
            
            if report["round_executed"]:
                agg_round = 1
                el_frac = report["eligible_fraction"]
                up_bytes = report["communication_bytes"]["uplink"]
                dn_bytes = report["communication_bytes"]["downlink"]
                div_before = report["divergence_before"]
                div_after = report["divergence_after"]
                for i in range(args.n_vehicles):
                    agents[i].online_net.load_state_dict(global_state)
                    # Reinstate optimizer to clear momentum
                    lr = agents[i].optimizer.param_groups[0]['lr']
                    agents[i].optimizer = optim.Adam(agents[i].online_net.parameters(), lr=lr)
                    agents[i].update_target_network() # Sync target
                print(f"[Ep {episode}] FedAvg Round: SUCCEEDED | Eligible: {report['eligible_fraction']*100:.1f}% | Div Before: {div_before:.4f} | Div After: {div_after:.4f}")
            else:
                print(f"[Ep {episode}] FedAvg Round: ABORTED | Eligible: {report['eligible_fraction']*100:.1f}%")
            
        # Evaluation
        if episode % args.eval_interval == 0:
            eval_metrics = evaluator.evaluate(agents, args.mode, args.eval_eps)
            
            print(f"[Ep {episode}] Eval Success: {eval_metrics['success_rate']:.3f} | Latency (succ): {eval_metrics['latency_success']:.4f}s | Energy: {eval_metrics['energy']:.4f}J")
            print(f"         Act Dist: L={eval_metrics['action_dist'][0]:.2f}, LTE={eval_metrics['action_dist'][1]:.2f}, 5G={eval_metrics['action_dist'][2]:.2f}")
            print(f"         TD Loss: {avg_td_loss:.4f} | Avg Q: {avg_q_val:.4f} | Eps: {current_eps:.3f}")
            
            # Save CSV
            with open(csv_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([episode, ep_reward, eval_metrics['success_rate'], eval_metrics['latency_success'], 
                                 eval_metrics['latency_all'], eval_metrics['energy'], eval_metrics['queue'], 
                                 current_eps, avg_td_loss, avg_q_val, agg_round, el_frac, up_bytes, dn_bytes,
                                 div_before if 'div_before' in locals() else 0.0,
                                 div_after if 'div_after' in locals() else 0.0,
                                 eval_metrics.get('success_disp', 0.0),
                                 eval_metrics.get('reward_disp', 0.0)])
                                 
            # Save Checkpoints
            if args.mode in ["shared", "independent", "fedavg"]:
                save_agent = agents[0] if args.mode == "shared" else agents[0] # Just saving client 0 for indep/fedavg
                
                os.makedirs(f"checkpoints_{args.mode}", exist_ok=True)
                
                save_agent.save(f"checkpoints_{args.mode}/seed_{args.seed}_episode_{episode:03d}.pt")
                if eval_metrics['success_rate'] > best_success:
                    best_success = eval_metrics['success_rate']
                    save_agent.save(f"checkpoints_{args.mode}/seed_{args.seed}_best.pt")
            
if __name__ == "__main__":
    train()
