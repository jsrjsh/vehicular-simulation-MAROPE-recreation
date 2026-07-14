# scripts/evaluate_federated.py
"""
Evaluation runner for multi-agent federated models.
Loads a global checkpoint under target environment/replay/privacy configurations
and evaluates it on V2XEnv.
"""

import os
import argparse
import csv
import numpy as np
from env.environment import V2XEnv
from agents.d3qn.agent import D3QNAgent

def main():
    parser = argparse.ArgumentParser(description="MA-ROPE Federated D3QN Evaluator")
    parser.add_argument("--environment-mode", type=str, choices=["baseline_recreation", "physically_corrected"],
                        default="physically_corrected", help="Simulation mode")
    parser.add_argument("--replay-mode", type=str, choices=["uniform", "prioritized"],
                        default="uniform", help="Replay buffer mode")
    parser.add_argument("--privacy-mode", type=str, choices=["none", "ldp_gaussian"],
                        default="none", help="LDP Mode")
    parser.add_argument("--epsilon", type=float, default=None, help="Round epsilon parameter")
    parser.add_argument("--delta", type=float, default=1e-5, help="Delta parameter")
    parser.add_argument("--n-agents", type=int, default=4, help="Number of vehicular agents")
    parser.add_argument("--episodes", type=int, default=5, help="Number of evaluation episodes")
    parser.add_argument("--seed", type=int, default=100, help="Random seed")
    parser.add_argument("--checkpoint-path", type=str, default="", help="Path to global checkpoint")
    
    args = parser.parse_args()
    
    if not args.checkpoint_path:
        if args.privacy_mode == "ldp_gaussian":
            mode_sub = f"ldp_gaussian/eps_{args.epsilon}_delta_{args.delta}"
        else:
            mode_sub = "none"
        args.checkpoint_path = f"checkpoints/{args.environment_mode}/{args.replay_mode}/{mode_sub}/global_checkpoint.pt"
        
    if not os.path.exists(args.checkpoint_path):
        raise FileNotFoundError(f"Global checkpoint not found at: {args.checkpoint_path}")

    print("==================================================")
    print(f"STARTING FEDERATED GLOBAL MODEL EVALUATION")
    print(f"Env: {args.environment_mode} | Replay: {args.replay_mode} | Privacy: {args.privacy_mode}")
    print(f"Checkpoint: {args.checkpoint_path}")
    print("==================================================")

    # Initialize env
    env = V2XEnv(
        n_vehicles=args.n_agents,
        scenario="urllc",
        max_steps=100,
        seed=args.seed,
        mode=args.environment_mode
    )

    # Initialize evaluation agents
    agents = []
    for idx in range(args.n_agents):
        agent = D3QNAgent(state_dim=12, action_dim=11, seed=args.seed + idx)
        agent.load(args.checkpoint_path)
        agents.append(agent)

    if args.privacy_mode == "ldp_gaussian":
        mode_sub = f"ldp_gaussian/eps_{args.epsilon}_delta_{args.delta}"
    else:
        mode_sub = "none"
        
    log_dir = f"logs/{args.environment_mode}/{args.replay_mode}/{mode_sub}"
    os.makedirs(log_dir, exist_ok=True)
    csv_file_path = f"{log_dir}/eval_stats.csv"
    
    csv_file = open(csv_file_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["episode", "mean_reward", "mean_latency_ms", "mean_energy_j", "mean_prr"])

    for ep in range(1, args.episodes + 1):
        obs_dict = env.reset(seed=args.seed + ep)
        ep_rewards = {i: 0.0 for i in range(args.n_agents)}
        ep_latencies = {i: [] for i in range(args.n_agents)}
        ep_energies = {i: [] for i in range(args.n_agents)}
        ep_successes = {i: [] for i in range(args.n_agents)}
        done = False
        
        while not done:
            action_dict = {}
            for i in range(args.n_agents):
                state = obs_dict[i]
                task = env.active_tasks[i]
                is_safety = (task["type"] == "safety")
                action_dict[i] = agents[i].select_action(state, is_safety_task=is_safety, evaluate=True)
                
            next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
            done = dones_dict[0]
            
            for i in range(args.n_agents):
                ep_rewards[i] += rewards_dict[i]
                ep_latencies[i].append(infos_dict[i]["latency_ms"])
                ep_energies[i].append(infos_dict[i]["energy_j"])
                ep_successes[i].append(1.0 if infos_dict[i]["transmission_success"] else 0.0)
                
            obs_dict = next_obs_dict

        mean_reward = np.mean(list(ep_rewards.values()))
        mean_lat = np.mean([l for client_lats in ep_latencies.values() for l in client_lats])
        mean_eng = np.mean([e for client_engs in ep_energies.values() for e in client_engs])
        mean_prr = np.mean([s for client_succs in ep_successes.values() for s in client_succs])
        
        print(f"Episode {ep:02d} | Reward: {mean_reward:.4f} | Latency: {mean_lat:.2f} ms | Energy: {mean_eng:.4f} J | Success: {mean_prr * 100:.1f}%")
        csv_writer.writerow([ep, mean_reward, mean_lat, mean_eng, mean_prr])
        
    csv_file.close()
    print(f"\nEvaluation stats logged to: {csv_file_path}")
    print("==================================================")

if __name__ == "__main__":
    main()
