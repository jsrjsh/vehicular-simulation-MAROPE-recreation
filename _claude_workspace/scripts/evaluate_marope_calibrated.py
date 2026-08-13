# scripts/evaluate_marope_calibrated.py
import os
import time
import hashlib
import csv
import numpy as np
import torch
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env.environment import V2XEnv
from env.config import TASK_TYPES
from agents.federated.coordinator import FederatedCoordinator

torch.set_num_threads(1)

def get_checkpoint_hash(weights_dict):
    hash_md5 = hashlib.md5()
    for k in sorted(weights_dict.keys()):
        hash_md5.update(weights_dict[k].cpu().numpy().tobytes())
    return hash_md5.hexdigest()[:8]

def train_ma_rope(env_mode, n_agents, seed, episodes=100, energy_mode="energy_legacy_unconverted", local_reliability_mode="local_success"):
    start_time = time.time()
    print(f"Training MA-ROPE ({env_mode}, {energy_mode}, {local_reliability_mode}, N={n_agents}, Seed={seed})...")
    
    env = V2XEnv(n_vehicles=n_agents, max_steps=100, seed=seed, mode=env_mode, policy_type="learned", energy_mode=energy_mode, local_reliability_mode=local_reliability_mode)
    coord = FederatedCoordinator(n_agents=n_agents, state_dim=12, action_dim=11, buffer_capacity=5000, batch_size=32, target_update_frequency=100, replay_mode="prioritized", participation_prob=0.9, seed=seed)
    
    step_count = 0
    for ep in range(1, episodes + 1):
        obs_dict = env.reset()
        done = False
        while not done:
            action_dict = {}
            for i in range(n_agents):
                state = obs_dict[i]
                is_safety = (env.active_tasks[i]["type"] == "safety")
                action_dict[i] = coord.agents[i].select_action(state, is_safety_task=is_safety)
                
            next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
            done = dones_dict[0] if isinstance(dones_dict, dict) and 0 in dones_dict else (dones_dict["__all__"] if "__all__" in dones_dict else list(dones_dict.values())[0])
            step_count += 1
            
            for i in range(n_agents):
                coord.agents[i].replay_buffer.add(obs_dict[i], action_dict[i], rewards_dict[i], next_obs_dict[i], done)
                coord.agents[i].learn()
                
            obs_dict = next_obs_dict
            
        # Aggregate at the end of each episode
        coord.aggregate_and_broadcast()
                
    ckpt_hash = get_checkpoint_hash(coord.agents[0].online_net.state_dict())
    print(f"Finished in {time.time() - start_time:.1f}s. Hash: {ckpt_hash}")
    return coord, ckpt_hash

def evaluate_policy(env_mode, policy_type, n_agents, seed, coord=None, episodes=5, energy_mode="energy_legacy_unconverted", local_reliability_mode="local_success"):
    env = V2XEnv(n_vehicles=n_agents, max_steps=100, seed=seed, mode=env_mode, policy_type=policy_type, energy_mode=energy_mode, local_reliability_mode=local_reliability_mode)
    
    ep_u_prr = []
    ep_u_otr = []
    ep_fleet_otr = []
    ep_prr = []
    ep_lat = []
    ep_eng = []
    
    for ep in range(1, episodes + 1):
        obs_dict = env.reset(seed=seed + 100 + ep)
        done = False
        
        step_u = []
        step_u_otr_vals = []
        step_lat = []
        step_eng = []
        tx_successes = []
        tx_on_times = []
        
        while not done:
            action_dict = {}
            for i in range(n_agents):
                if policy_type == "ma-rope" and coord is not None:
                    is_safety = (env.active_tasks[i]["type"] == "safety")
                    action_dict[i] = coord.agents[i].select_action(obs_dict[i], is_safety_task=is_safety, evaluate=True)
                elif policy_type == "alloffload":
                    action_dict[i] = 8
                else: # nooffload
                    action_dict[i] = 0
                    
            next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
            done = dones_dict["__all__"] if "__all__" in dones_dict else list(dones_dict.values())[0]
            
            for i in range(n_agents):
                info = infos_dict[i]
                active_rng = np.random.RandomState(seed + ep * 1000 + env.episode_step * 10 + i)
                is_active = (active_rng.uniform(0.0, 1.0) < 0.3)
                
                if is_active:
                    step_u.append(rewards_dict[i])
                    step_u_otr_vals.append(info["u_otr"])
                    step_lat.append(info["latency_ms"])
                    step_eng.append(info["energy_j"])
                
                if info["chosen_rat"] > 0 and info["chosen_rho"] > 0.0:
                    tx_successes.append(1.0 if info["transmission_success"] else 0.0)
                    tx_on_times.append(1.0 if (info["transmission_success"] and info["latency_ms"] <= TASK_TYPES[info["task_type"]]["D_ms"]) else 0.0)
            
            obs_dict = next_obs_dict
            
        ep_u_prr.append(np.mean(step_u) if step_u else 0.0)
        ep_u_otr.append(np.mean(step_u_otr_vals) if step_u_otr_vals else 0.0)
        ep_lat.append(np.mean(step_lat) if step_lat else 0.0)
        ep_eng.append(np.mean(step_eng) if step_eng else 0.0)
        ep_fleet_otr.append(np.mean(tx_on_times) if tx_on_times else 1.0)
        ep_prr.append(np.mean(tx_successes) if tx_successes else 1.0)
        
    return {
        "u_prr": np.mean(ep_u_prr),
        "u_otr": np.mean(ep_u_otr),
        "fleet_otr": np.mean(ep_fleet_otr),
        "prr": np.mean(ep_prr),
        "latency": np.mean(ep_lat),
        "energy": np.mean(ep_eng)
    }

def main():
    seeds = [0, 1, 2, 3, 4]
    mode = "manuscript_calibrated"
    
    n32_targets = {
        "ma-rope": {"u_prr": 0.8323, "energy": 0.7057, "latency": 213.0},
        "alloffload": {"u_prr": 0.7790, "energy": 0.9441, "latency": 176.9},
        "nooffload": {"u_prr": 0.8442, "energy": 0.5032, "latency": 248.1}
    }
    
    results = {8: {}, 32: {}}
    for n in [8, 32]:
        for p in ["ma-rope", "alloffload", "nooffload"]:
            results[n][p] = []
            
    for n_agents in [8, 32]:
        for policy in ["ma-rope", "alloffload", "nooffload"]:
            for seed in seeds:
                if policy == "ma-rope":
                    coord, _ = train_ma_rope(mode, n_agents, seed, episodes=100)
                    metrics = evaluate_policy(mode, policy, n_agents, seed, coord=coord)
                else:
                    metrics = evaluate_policy(mode, policy, n_agents, seed)
                results[n_agents][policy].append(metrics)
                
    # Write report
    report = "# MANUSCRIPT_CALIBRATED_POLICY_REPORT.md\n\n"
    report += "This document verifies the training outcomes of MA-ROPE under the `manuscript_calibrated` environment.\n\n"
    
    report += "## N=32 Results\n\n"
    report += "| Policy | Metric | Target | Simulated | Status |\n"
    report += "| :--- | :--- | :---: | :---: | :---: |\n"
    
    for p in ["ma-rope", "alloffload", "nooffload"]:
        metrics = results[32][p]
        u_mean = np.mean([r["u_prr"] for r in metrics])
        e_mean = np.mean([r["energy"] for r in metrics])
        l_mean = np.mean([r["latency"] for r in metrics])
        
        t = n32_targets[p]
        def fmt(sim, tar):
            status = "PASS" if abs(sim - tar) / tar <= 0.05 else "WARNING"
            return f"{sim:.4f} | **{status}**"
            
        report += f"| {p.upper()} | U_PRR | {t['u_prr']:.4f} | {fmt(u_mean, t['u_prr'])} |\n"
        report += f"| {p.upper()} | Energy | {t['energy']:.4f} | {fmt(e_mean, t['energy'])} |\n"
        report += f"| {p.upper()} | Latency | {t['latency']:.1f} | {fmt(l_mean, t['latency'])} |\n"
        
    with open("MANUSCRIPT_CALIBRATED_POLICY_REPORT.md", "w") as f:
        f.write(report)
        
    print("Sweep complete. Generated MANUSCRIPT_CALIBRATED_POLICY_REPORT.md")

if __name__ == "__main__":
    main()
