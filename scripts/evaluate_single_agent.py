# scripts/evaluate_single_agent.py
"""
Evaluation runner for single-agent D3QN.
Loads a checkpoint, runs evaluation episodes with exploration set to 0.05,
and logs metrics to CSV.
"""

import os
import argparse
import csv
import numpy as np
from env.environment import V2XEnv
from agents.d3qn.agent import D3QNAgent

def main():
    parser = argparse.ArgumentParser(description="MA-ROPE Single-Agent D3QN Evaluator")
    parser.add_argument("--environment-mode", type=str, choices=["baseline_recreation", "physically_corrected"],
                        default="physically_corrected", help="Simulation mode")
    parser.add_argument("--episodes", type=int, default=5, help="Number of evaluation episodes")
    parser.add_argument("--seed", type=int, default=100, help="Random seed")
    parser.add_argument("--checkpoint-path", type=str, default="", help="Path to checkpoint file")
    
    args = parser.parse_args()
    
    if not args.checkpoint_path:
        args.checkpoint_path = f"checkpoints/{args.environment_mode}/checkpoint.pt"
        
    if not os.path.exists(args.checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found at: {args.checkpoint_path}")

    print("==================================================")
    print(f"STARTING SINGLE-AGENT EVALUATION (Mode: {args.environment_mode})")
    print(f"Checkpoint: {args.checkpoint_path}")
    print("==================================================")

    # Initialize env
    env = V2XEnv(
        n_vehicles=1,
        scenario="urllc",
        max_steps=100,
        seed=args.seed,
        mode=args.environment_mode
    )

    # Initialize agent
    agent = D3QNAgent(
        state_dim=12,
        action_dim=11,
        seed=args.seed
    )
    
    # Load weights
    agent.load(args.checkpoint_path)

    log_dir = f"logs/{args.environment_mode}"
    os.makedirs(log_dir, exist_ok=True)
    csv_file_path = f"{log_dir}/eval_stats.csv"
    
    csv_file = open(csv_file_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["episode", "total_reward", "mean_latency_ms", "mean_energy_j", "prr_success_rate"])

    rewards = []
    latencies = []
    energies = []
    successes = []

    for ep in range(1, args.episodes + 1):
        # Episode reset seed: seed + episode_index
        obs_dict = env.reset(seed=args.seed + ep)
        state = obs_dict[0]
        
        ep_reward = 0.0
        ep_latencies = []
        ep_energies = []
        ep_successes = []
        done = False
        
        while not done:
            task = env.active_tasks[0]
            is_safety = (task["type"] == "safety")
            
            # Action selection with evaluation flag (epsilon = 0.05)
            action = agent.select_action(state, is_safety_task=is_safety, evaluate=True)
            
            next_obs, rewards_dict, dones, infos = env.step({0: action})
            
            next_state = next_obs[0]
            reward = rewards_dict[0]
            done = dones[0]
            
            ep_latencies.append(infos[0]["latency_ms"])
            ep_energies.append(infos[0]["energy_j"])
            ep_successes.append(1.0 if infos[0]["transmission_success"] else 0.0)
            
            state = next_state
            ep_reward += reward

        mean_lat = np.mean(ep_latencies)
        mean_eng = np.mean(ep_energies)
        prr_rate = np.mean(ep_successes)
        
        print(f"Episode {ep:02d} | Reward: {ep_reward:.4f} | Latency: {mean_lat:.2f} ms | Energy: {mean_eng:.4f} J | Success: {prr_rate * 100:.1f}%")
        csv_writer.writerow([ep, ep_reward, mean_lat, mean_eng, prr_rate])
        
        rewards.append(ep_reward)
        latencies.append(mean_lat)
        energies.append(mean_eng)
        successes.append(prr_rate)

    csv_file.close()
    
    print("\n==================================================")
    print(f"Evaluation finished across {args.episodes} episodes:")
    print(f"Average Reward: {np.mean(rewards):.4f}")
    print(f"Average Latency: {np.mean(latencies):.2f} ms")
    print(f"Average Energy: {np.mean(energies):.4f} J")
    print(f"Average PRR Sidelink Success: {np.mean(successes) * 100:.1f}%")
    print(f"Evaluation logs written to: {csv_file_path}")
    print("==================================================")

if __name__ == "__main__":
    main()
