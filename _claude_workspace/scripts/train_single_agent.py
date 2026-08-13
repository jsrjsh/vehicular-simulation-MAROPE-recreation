# scripts/train_single_agent.py
"""
Training runner for a single-agent D3QN in the V2X environment.
Supports '--environment-mode' and '--replay-mode' configurations.
Includes comparative deterministic learning fixture and smoke training runs.
"""

import os
import argparse
import csv
import math
import numpy as np
import torch
from env.environment import V2XEnv
from agents.d3qn.agent import D3QNAgent

def run_learning_fixture(replay_mode: str):
    """
    Tiny deterministic learning fixture.
    1-state MDP where action 8 yields reward 1.0, and all other actions yield 0.0.
    Verifies that the D3QN agent reliably learns the preferred action across 5 seeds.
    """
    print(f"Running learning fixture for replay mode: {replay_mode}...")
    
    seeds = [0, 1, 2, 3, 4]
    all_success = True
    results = {}
    
    for seed in seeds:
        # Initialize agent
        agent = D3QNAgent(
            state_dim=12,
            action_dim=11,
            lr=1e-3,
            batch_size=8,
            target_update_frequency=10,
            replay_mode=replay_mode,
            seed=seed
        )
        
        # Train on the 1-state MDP
        state = np.zeros(12, dtype=np.float32)
        next_state = np.zeros(12, dtype=np.float32)
        
        steps_taken = 0
        learned = False
        
        for step in range(150):
            action = agent.select_action(state)
            reward = 1.0 if action == 8 else 0.0
            done = True
            
            # Record transition
            agent.replay_buffer.add(state, action, reward, next_state, done)
            
            # Learn
            if len(agent.replay_buffer) >= agent.batch_size:
                agent.learn()
                steps_taken += 1
                
            # Check if optimal action is chosen greedily
            if agent.select_action(state, evaluate=True) == 8 and not learned:
                learned = True
                results[seed] = steps_taken
                
        # Final check
        final_action = agent.select_action(state, evaluate=True)
        if final_action != 8:
            all_success = False
            results[seed] = -1  # Failed to learn
            
    return all_success, results

def main():
    parser = argparse.ArgumentParser(description="MA-ROPE Single-Agent D3QN Trainer")
    parser.add_argument("--environment-mode", type=str, choices=["baseline_recreation", "physically_corrected"],
                        default="physically_corrected", help="Simulation mode")
    parser.add_argument("--replay-mode", type=str, choices=["uniform", "prioritized"],
                        default="uniform", help="Experience replay mode")
    parser.add_argument("--episodes", type=int, default=30, help="Number of training episodes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--run-fixture", action="store_true", help="Run the tiny learning fixture first")
    
    args = parser.parse_args()
    
    if args.run_fixture:
        print("==================================================")
        print("RUNNING TINY DETERMINISTIC LEARNING FIXTURE")
        print("==================================================")
        success, results = run_learning_fixture(args.replay_mode)
        for seed, steps in results.items():
            status = f"Learned in {steps} steps" if steps >= 0 else "FAILED"
            print(f"Seed {seed}: {status}")
        if not success:
            print("Learning fixture failed. Exiting.")
            return

    print("==================================================")
    print(f"STARTING SINGLE-AGENT SMOKE TRAINING (Env: {args.environment_mode} | Replay: {args.replay_mode})")
    print("==================================================")

    # Initialize single-agent V2X environment
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
        gamma=0.95,
        lr=1e-3,
        buffer_capacity=5000,
        batch_size=32,
        target_update_frequency=50,
        replay_mode=args.replay_mode,
        seed=args.seed
    )

    # Log directories (isolate by environment-mode and replay-mode)
    log_dir = f"logs/{args.environment_mode}/{args.replay_mode}"
    checkpoint_dir = f"checkpoints/{args.environment_mode}/{args.replay_mode}"
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
            
            agent.replay_buffer.add(state, action, reward, next_state, done)
            loss, _q_val = agent.learn()  # BUGFIX (Claude, 2026-08-02): agent.learn() returns a
            # (loss, mean_q) tuple, not a scalar (see agents/d3qn/agent.py return statement and
            # its correct usage in scripts/train_b3_baselines.py). The prior `loss = agent.learn()`
            # would raise TypeError on `if loss > 0.0` the first time the replay buffer reached
            # batch_size, i.e. this script could not have completed a real training run as-is.
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
