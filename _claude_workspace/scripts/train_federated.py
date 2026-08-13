# scripts/train_federated.py
"""
Federated Learning training runner for MA-ROPE.
Supports '--environment-mode', '--replay-mode', and LDP '--privacy-mode' parameters.
Includes the comparative learning fixtures and privacy-utility sweep logs.
"""

import os
import argparse
import csv
import copy
import math
import numpy as np
import torch
from env.environment import V2XEnv
from agents.federated.coordinator import FederatedCoordinator
from agents.d3qn.agent import D3QNAgent

def run_controlled_fixture():
    """
    Deterministic comparative federated learning fixture.
    Compares: (1) No Privacy, (2) Weak Privacy, (3) Moderate Privacy, (4) Strong Privacy.
    Evaluates learning capability on 1-state MDP across 5 independent seeds.
    """
    print("==================================================")
    print("RUNNING PRIVACY COMPARATIVE SANITY FIXTURE")
    print("==================================================")
    
    seeds = [0, 1, 2, 3, 4]
    steps = 100
    
    # State vectors for 3 distinct clients
    s0 = np.zeros(12, dtype=np.float32)
    s1 = np.ones(12, dtype=np.float32)
    s2 = np.ones(12, dtype=np.float32) * 2.0
    states = [s0, s1, s2]
    
    privacy_levels = {
        "no_privacy": {"mode": "none", "sigma": 0.0, "C": 5.0},
        "weak_privacy": {"mode": "ldp_gaussian", "sigma": 0.1, "C": 5.0},
        "mod_privacy": {"mode": "ldp_gaussian", "sigma": 0.5, "C": 5.0},
        "strong_privacy": {"mode": "ldp_gaussian", "sigma": 2.0, "C": 5.0}
    }
    
    for lvl_name, lvl_cfg in privacy_levels.items():
        print(f"\n--- Testing Privacy Level: {lvl_name} (Sigma: {lvl_cfg['sigma']}, C: {lvl_cfg['C']}) ---")
        
        success_seeds = 0
        for seed in seeds:
            coord = FederatedCoordinator(
                n_agents=3,
                batch_size=8,
                target_update_frequency=10,
                participation_prob=1.0,
                privacy_mode=lvl_cfg["mode"],
                clip_norm=lvl_cfg["C"],
                noise_multiplier=lvl_cfg["sigma"],
                seed=seed
            )
            
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
                    
            # Check if all clients greedily pick action 8
            choices = [coord.agents[i].select_action(states[i], evaluate=True) for i in range(3)]
            if choices == [8, 8, 8]:
                success_seeds += 1
                
        print(f"Result {lvl_name}: {success_seeds}/5 Seeds converged to optimal action.")
        
    return True

def main():
    parser = argparse.ArgumentParser(description="MA-ROPE Synchronous FedAvg Trainer")
    parser.add_argument("--environment-mode", type=str, choices=["baseline_recreation", "physically_corrected"],
                        default="physically_corrected", help="Simulation mode")
    parser.add_argument("--replay-mode", type=str, choices=["uniform", "prioritized"],
                        default="uniform", help="Experience replay mode")
    
    # Privacy Arguments
    parser.add_argument("--privacy-mode", type=str, choices=["none", "ldp_gaussian"],
                        default="none", help="LDP Mode")
    parser.add_argument("--clip-norm", type=float, default=5.0, help="LDP clipping threshold C")
    parser.add_argument("--noise-multiplier", type=float, default=0.0, help="LDP Gaussian multiplier sigma")
    parser.add_argument("--epsilon", type=float, default=None, help="LDP round privacy epsilon")
    parser.add_argument("--delta", type=float, default=1e-5, help="LDP probability delta")
    
    parser.add_argument("--n-agents", type=int, default=4, help="Number of vehicular agents")
    parser.add_argument("--sync-interval", type=int, default=20, help="Federation synchronization interval")
    parser.add_argument("--participation-prob", type=float, default=0.9, help="Client participation probability")
    parser.add_argument("--episodes", type=int, default=15, help="Number of training episodes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--run-fixture", action="store_true", help="Run comparative privacy sanity fixture first")
    
    args = parser.parse_args()
    
    if args.run_fixture:
        run_controlled_fixture()
        return

    # Derive noise multiplier if epsilon is explicitly defined
    nominal_epsilon = "none"
    if args.privacy_mode == "ldp_gaussian" and args.epsilon is not None:
        nominal_epsilon = args.epsilon
        # Gaussian mechanism conversion: sigma = sqrt(2 * ln(1.25/delta)) / epsilon
        derived_sigma = math.sqrt(2.0 * math.log(1.25 / args.delta)) / args.epsilon
        print(f"[LDP Parameterizer] Derived noise multiplier sigma = {derived_sigma:.4f} from epsilon={args.epsilon}, delta={args.delta}")
        args.noise_multiplier = derived_sigma

    # Isolate directories
    if args.privacy_mode == "ldp_gaussian":
        mode_sub = f"ldp_gaussian/eps_{args.epsilon}_delta_{args.delta}"
    else:
        mode_sub = "none"
        
    log_dir = f"logs/{args.environment_mode}/{args.replay_mode}/{mode_sub}"
    checkpoint_dir = f"checkpoints/{args.environment_mode}/{args.replay_mode}/{mode_sub}"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(checkpoint_dir, exist_ok=True)

    print("==================================================")
    print(f"STARTING FEDERATED SMOKE TRAINING")
    print(f"Env: {args.environment_mode} | Replay: {args.replay_mode} | Privacy: {args.privacy_mode} (Eps: {nominal_epsilon})")
    print("==================================================")

    # Initialize environment
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
        privacy_mode=args.privacy_mode,
        clip_norm=args.clip_norm,
        noise_multiplier=args.noise_multiplier,
        seed=args.seed
    )

    # Training Curves
    train_stats_path = f"{log_dir}/train_stats.csv"
    train_file = open(train_stats_path, "w", newline="")
    train_writer = csv.writer(train_file)
    train_writer.writerow(["episode", "mean_reward", "mean_loss"])

    # Comm logs file
    comm_stats_path = f"{log_dir}/communication_stats.csv"
    comm_file = open(comm_stats_path, "w", newline="")
    comm_writer = csv.writer(comm_file)
    comm_writer.writerow(["round", "active_agents", "ratio", "aborted", "bytes_this_round", "cum_bytes"])

    # Privacy stats file
    privacy_stats_path = f"{log_dir}/privacy_stats.csv"
    priv_file = open(privacy_stats_path, "w", newline="")
    priv_writer = csv.writer(priv_file)
    priv_writer.writerow(["round", "client_idx", "raw_norm", "clipped_norm", "noise_norm", "snr", "clipped"])

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
                
                agent = coordinator.agents[i]
                agent.replay_buffer.add(state, action, reward, next_state, v_done)
                loss, _q_val = agent.learn()  # BUGFIX (Claude, 2026-08-02): see train_single_agent.py
                # — agent.learn() returns (loss, mean_q), not a scalar; unpacking fixes a TypeError
                # that would otherwise crash this script once the replay buffer reached batch_size.
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
                
                # Write LDP client stats
                if not round_info["aborted"] and args.privacy_mode == "ldp_gaussian":
                    for client_idx, c_stats in round_info["clients"].items():
                        priv_writer.writerow([
                            round_info["round"],
                            client_idx,
                            c_stats["raw_norm"],
                            c_stats["clipped_norm"],
                            c_stats["noise_norm"],
                            c_stats["snr"],
                            c_stats["clipped"]
                        ])
                    priv_file.flush()

        mean_reward = np.mean(list(ep_rewards.values()))
        flat_losses = [l for client_losses in losses.values() for l in client_losses]
        mean_loss = np.mean(flat_losses) if flat_losses else 0.0
        
        print(f"Episode {ep:02d} | Mean Reward: {mean_reward:.4f} | Mean Loss: {mean_loss:.4f}")
        train_writer.writerow([ep, mean_reward, mean_loss])
        train_file.flush()

    train_file.close()
    comm_file.close()
    priv_file.close()
    
    # Save global online network weights from agent 0 (synchronized)
    global_checkpoint_path = f"{checkpoint_dir}/global_checkpoint.pt"
    coordinator.agents[0].save(global_checkpoint_path)
    print(f"Training stats saved to: {train_stats_path}")
    print(f"Communication metrics saved to: {comm_stats_path}")
    print(f"Global model checkpoint saved to: {global_checkpoint_path}")

if __name__ == "__main__":
    main()
