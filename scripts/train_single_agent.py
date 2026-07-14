# scripts/train_single_agent.py
"""
Training runner for a single-agent D3QN in the V2X environment.
Supports '--environment-mode' configuration and logs results.
Includes a tiny deterministic learning fixture to verify learning capabilities.
"""

import os
import argparse
import csv
import math
import numpy as np
import torch
from env.environment import V2XEnv
from agents.d3qn.agent import D3QNAgent

def run_learning_fixture():
    """
    Tiny deterministic learning fixture.
    1-state MDP where action 8 yields reward 1.0, and all other actions yield 0.0.
    Verifies that the D3QN agent reliably learns the preferred action across 5 seeds.
    """
    print("==================================================")
    print("RUNNING TINY DETERMINISTIC LEARNING FIXTURE")
    print("==================================================")
    
    seeds = [0, 1, 2, 3, 4]
    all_success = True
    
    for seed in seeds:
        # Initialize agent
        agent = D3QNAgent(
            state_dim=12,
            action_dim=11,
            lr=1e-3,
            batch_size=8,
            target_update_frequency=10,
            seed=seed
        )
        
        # Train on the 1-state MDP
        # State is constant, reward is 1.0 for action 8, 0.0 otherwise
        state = np.zeros(12, dtype=np.float32)
        next_state = np.zeros(12, dtype=np.float32)
        
        for step in range(150):
            is_safety = False
            # Action selection
            action = agent.select_action(state, is_safety_task=is_safety)
            reward = 1.0 if action == 8 else 0.0
            done = True
            
            # Record transition
            agent.replay_buffer.add(state, action, reward, next_state, done)
            
            # Learn
            if len(agent.replay_buffer) >= agent.batch_size:
                agent.learn()
                
        # Evaluate greedy action (epsilon = 0.0)
        final_action = agent.select_action(state, evaluate=True)
        print(f"Seed {seed}: Final Selected Action = {final_action} (Expected: 8)")
        if final_action != 8:
            all_success = False
            
    if all_success:
        print("RESULT: SUCCESS - D3QN reliably learned optimal action across all seeds.")
    else:
        print("RESULT: FAILURE - D3QN failed to learn optimal action on one or more seeds.")
    return all_success

def main():
    parser = argparse.ArgumentParser(description="MA-ROPE Single-Agent D3QN Trainer")
    parser.add_argument("--environment-mode", type=str, choices=["baseline_recreation", "physically_corrected"],
                        default="physically_corrected", help="Simulation mode")
    parser.add_argument("--episodes", type=int, default=30, help="Number of training episodes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--run-fixture", action="store_true", help="Run the tiny learning fixture first")
    
    args = parser.parse_args()
    
    if args.run_fixture:
        success = run_learning_fixture()
        if not success:
            print("Learning fixture failed. Exiting.")
            return

    print("==================================================")
    print(f"STARTING SINGLE-AGENT SMOKE TRAINING (Mode: {args.environment_mode})")
    print("==================================================")

    # Initialize single-agent V2X environment
    env = V2XEnv(
        n_vehicles=1,
        scenario="urllc",
        max_steps=100,  # short episodes
        seed=args.seed,
        mode=args.environment_mode
    )

    # Initialize agent
    agent = D3QNAgent(
        state_dim=12,
        action_dim=11,
        gamma=0.95,
        lr=1e-3,
        buffer_capacity=5000,
        batch_size=32,
        target_update_frequency=50,
        seed=args.seed
    )

    # Log directories
    log_dir = f"logs/{args.environment_mode}"
    checkpoint_dir = f"checkpoints/{args.environment_mode}"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    csv_file_path = f"{log_dir}/train_stats.csv"
    csv_file = open(csv_file_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["episode", "total_reward", "mean_loss", "epsilon"])

    # Training Loop
    for ep in range(1, args.episodes + 1):
        obs_dict = env.reset()
        state = obs_dict[0]
        
        ep_reward = 0.0
        losses = []
        done = False
        
        while not done:
            task = env.active_tasks[0]
            is_safety = (task["type"] == "safety")
            
            action = agent.select_action(state, is_safety_task=is_safety)
            
            next_obs, rewards, dones, infos = env.step({0: action})
            
            next_state = next_obs[0]
            reward = rewards[0]
            done = dones[0]
            
            # Record transition
            agent.replay_buffer.add(state, action, reward, next_state, done)
            
            # Gradient step
            loss = agent.learn()
            if loss > 0.0:
                losses.append(loss)
                
            state = next_state
            ep_reward += reward

        mean_loss = np.mean(losses) if losses else 0.0
        print(f"Episode {ep:02d} | Reward: {ep_reward:.4f} | Loss: {mean_loss:.4f} | Epsilon: {agent.epsilon:.4f}")
        csv_writer.writerow([ep, ep_reward, mean_loss, agent.epsilon])
        csv_file.flush()

    csv_file.close()
    
    # Save checkpoint
    checkpoint_path = f"{checkpoint_dir}/checkpoint.pt"
    agent.save(checkpoint_path)
    print(f"Training stats saved to: {csv_file_path}")
    print(f"Model checkpoint saved to: {checkpoint_path}")

if __name__ == "__main__":
    main()
