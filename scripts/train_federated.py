# scripts/train_federated.py
"""
Federated Learning training runner for MA-ROPE.
Supports '--environment-mode' and '--replay-mode' isolated configs.
Includes the controlled comparative fixture and communications metrics logging.
"""

import os
import argparse
import csv
import copy
import numpy as np
import torch
from env.environment import V2XEnv
from agents.federated.coordinator import FederatedCoordinator
from agents.d3qn.agent import D3QNAgent

def run_controlled_fixture():
    """
    Deterministic comparative federated learning fixture.
    Compares: (1) Isolated local training, (2) Centralized pooled training, (3) Synchronous FedAvg.
    Clients have non-identical state vectors representing distinct data distributions.
    """
    print("==================================================")
    print("RUNNING CONTROLLED FEDERATED LEARNING FIXTURE")
    print("==================================================")
    
    seeds = [10, 20, 30]
    steps = 100
    
    # State vectors for 3 distinct clients
    s0 = np.zeros(12, dtype=np.float32)
    s1 = np.ones(12, dtype=np.float32)
    s2 = np.ones(12, dtype=np.float32) * 2.0
    states = [s0, s1, s2]
    
    # Helper to calculate weight divergence (Frobenius norm) between client online nets
    def calc_divergence(net1, net2):
        dist = 0.0
        for p1, p2 in zip(net1.parameters(), net2.parameters()):
            dist += torch.sum((p1 - p2) ** 2).item()
        return math.sqrt(dist)

    import math

    # --- 1. Isolated Local Training ---
    print("\n--- Running Isolated Local Training ---")
    isolated_agents = [
        D3QNAgent(state_dim=12, action_dim=11, batch_size=8, target_update_frequency=10, seed=s)
        for s in seeds
    ]
    for step in range(steps):
        for idx, agent in enumerate(isolated_agents):
            state = states[idx]
            action = agent.select_action(state)
            reward = 1.0 if action == 8 else 0.0
            agent.replay_buffer.add(state, action, reward, state, True)
            if len(agent.replay_buffer) >= agent.batch_size:
                agent.learn()
                
    iso_choices = [agent.select_action(states[i], evaluate=True) for i, agent in enumerate(isolated_agents)]
    print(f"Isolated Final Actions: {iso_choices} (Expected: [8, 8, 8])")

    # --- 2. Centralized Pooled Training ---
    print("\n--- Running Centralized Pooled Training ---")
    pooled_agent = D3QNAgent(state_dim=12, action_dim=11, batch_size=8, target_update_frequency=10, seed=42)
    for step in range(steps):
        for idx in range(3):
            state = states[idx]
            action = pooled_agent.select_action(state)
            reward = 1.0 if action == 8 else 0.0
            # Put all client data in one centralized buffer
            pooled_agent.replay_buffer.add(state, action, reward, state, True)
            if len(pooled_agent.replay_buffer) >= pooled_agent.batch_size:
                pooled_agent.learn()
                
    pooled_choices = [pooled_agent.select_action(states[i], evaluate=True) for i in range(3)]
    print(f"Centralized Final Actions: {pooled_choices} (Expected: [8, 8, 8])")

    # --- 3. Synchronous FedAvg ---
    print("\n--- Running Synchronous FedAvg Training ---")
    coord = FederatedCoordinator(
        n_agents=3,
        batch_size=8,
        target_update_frequency=10,
        participation_prob=1.0,  # 100% participation for fixture
        seed=42
    )
    # Sync every 10 steps
    for step in range(steps):
        for idx in range(3):
            agent = coord.agents[idx]
            state = states[idx]
            action = agent.select_action(state)
            reward = 1.0 if action == 8 else 0.0
            agent.replay_buffer.add(state, action, reward, state, True)
            if len(agent.replay_buffer) >= agent.batch_size:
                agent.learn()
                
        if (step + 1) % 10 == 0:
            coord.aggregate_and_broadcast()
            
    fed_choices = [coord.agents[i].select_action(states[i], evaluate=True) for i in range(3)]
    print(f"FedAvg Final Actions: {fed_choices} (Expected: [8, 8, 8])")

    # Compare divergences
    div_iso = calc_divergence(isolated_agents[0].online_net, isolated_agents[1].online_net)
    div_fed = calc_divergence(coord.agents[0].online_net, coord.agents[1].online_net)
    print(f"\nDivergence Client 0-1 (Isolated): {div_iso:.4f}")
    print(f"Divergence Client 0-1 (FedAvg): {div_fed:.4f} (Expected: 0.0 due to weight sync)")

    return True

def main():
    parser = argparse.ArgumentParser(description="MA-ROPE Synchronous FedAvg Trainer")
    parser.add_argument("--environment-mode", type=str, choices=["baseline_recreation", "physically_corrected"],
                        default="physically_corrected", help="Simulation mode")
    parser.add_argument("--replay-mode", type=str, choices=["uniform", "prioritized"],
                        default="uniform", help="Experience replay mode")
    parser.add_argument("--n-agents", type=int, default=4, help="Number of vehicular agents")
    parser.add_argument("--sync-interval", type=int, default=20, help="Federation synchronization interval")
    parser.add_argument("--participation-prob", type=float, default=0.9, help="Client participation probability")
    parser.add_argument("--episodes", type=int, default=15, help="Number of training episodes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--run-fixture", action="store_true", help="Run comparative controlled fixture first")
    
    args = parser.parse_args()
    
    if args.run_fixture:
        run_controlled_fixture()
        return

    print("==================================================")
    print(f"STARTING FEDERATED SMOKE TRAINING")
    print(f"Env: {args.environment_mode} | Replay: {args.replay_mode} | Agents: {args.n_agents} | Sync Interval: {args.sync_interval}")
    print("==================================================")

    # Initialize environment with N vehicles matching N agents
    env = V2XEnv(
        n_vehicles=args.n_agents,
        scenario="urllc",
        max_steps=100,
        seed=args.seed,
        mode=args.environment_mode
    )

    # Initialize coordinator
    coordinator = FederatedCoordinator(
        n_agents=args.n_agents,
        state_dim=12,
        action_dim=11,
        gamma=0.95,
        lr=1e-3,
        buffer_capacity=5000,
        batch_size=32,
        target_update_frequency=50,
        replay_mode=args.replay_mode,
        participation_prob=args.participation_prob,
        seed=args.seed
    )

    # Isolated log/checkpoint directories
    log_dir = f"logs/{args.environment_mode}/{args.replay_mode}/federated"
    checkpoint_dir = f"checkpoints/{args.environment_mode}/{args.replay_mode}/federated"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Train curves file
    train_stats_path = f"{log_dir}/train_stats.csv"
    train_file = open(train_stats_path, "w", newline="")
    train_writer = csv.writer(train_file)
    train_writer.writerow(["episode", "mean_reward", "mean_loss"])

    # Comm logs file
    comm_stats_path = f"{log_dir}/communication_stats.csv"
    comm_file = open(comm_stats_path, "w", newline="")
    comm_writer = csv.writer(comm_file)
    comm_writer.writerow(["round", "active_agents", "ratio", "aborted", "bytes_this_round", "cum_bytes"])

    step_count = 0

    # Training Loop
    for ep in range(1, args.episodes + 1):
        obs_dict = env.reset()
        ep_rewards = {i: 0.0 for i in range(args.n_agents)}
        losses = {i: [] for i in range(args.n_agents)}
        done = False
        
        while not done:
            action_dict = {}
            for i in range(args.n_agents):
                state = obs_dict[i]
                task = env.active_tasks[i]
                is_safety = (task["type"] == "safety")
                action_dict[i] = coordinator.agents[i].select_action(state, is_safety_task=is_safety)
                
            next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
            done = dones_dict[0]
            step_count += 1
            
            # Local update loop
            for i in range(args.n_agents):
                state = obs_dict[i]
                action = action_dict[i]
                reward = rewards_dict[i]
                next_state = next_obs_dict[i]
                v_done = dones_dict[i]
                
                # Insert and Learn locally
                agent = coordinator.agents[i]
                agent.replay_buffer.add(state, action, reward, next_state, v_done)
                loss = agent.learn()
                if loss > 0.0:
                    losses[i].append(loss)
                    
                ep_rewards[i] += reward
                
            obs_dict = next_obs_dict
            
            # Synchronous FedAvg check
            if step_count % args.sync_interval == 0:
                round_info = coordinator.aggregate_and_broadcast()
                comm_writer.writerow([
                    round_info["round"],
                    round_info["active_agents"],
                    round_info["ratio"],
                    round_info["aborted"],
                    round_info["bytes_transferred"],
                    coordinator.cum_bytes
                ])
                comm_file.flush()

        mean_reward = np.mean(list(ep_rewards.values()))
        flat_losses = [l for client_losses in losses.values() for l in client_losses]
        mean_loss = np.mean(flat_losses) if flat_losses else 0.0
        
        print(f"Episode {ep:02d} | Mean Reward: {mean_reward:.4f} | Mean Loss: {mean_loss:.4f}")
        train_writer.writerow([ep, mean_reward, mean_loss])
        train_file.flush()

    train_file.close()
    comm_file.close()
    
    # Save global online network weights from agent 0 (synchronized)
    global_checkpoint_path = f"{checkpoint_dir}/global_checkpoint.pt"
    coordinator.agents[0].save(global_checkpoint_path)
    print(f"Training stats saved to: {train_stats_path}")
    print(f"Communication metrics saved to: {comm_stats_path}")
    print(f"Global model checkpoint saved to: {global_checkpoint_path}")

if __name__ == "__main__":
    main()
