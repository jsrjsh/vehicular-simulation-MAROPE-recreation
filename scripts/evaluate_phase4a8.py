import os
import sys
import numpy as np
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env.environment import V2XEnv
from scripts.evaluate_marope_calibrated import train_ma_rope
import torch

MODES = ["local_success", "local_neutral"]

def custom_eval(env_mode, policy_type, n_agents, seed, coord=None, episodes=5, energy_mode="energy_si_corrected", local_reliability_mode="local_success"):
    env = V2XEnv(n_vehicles=n_agents, max_steps=100, seed=seed, mode=env_mode, policy_type=policy_type, energy_mode=energy_mode, local_reliability_mode=local_reliability_mode)
    
    metrics = {
        "u_prr": [], "u_otr": [], "fleet_otr": [], "prr": [], "lat": [], "eng": [],
        "actions": {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0},
        "rhos": [], "local_frac": 0, "partial_frac": 0, "full_frac": 0, "total_decisions": 0,
        "queue_loss": []
    }
    
    for ep in range(1, episodes + 1):
        obs_dict = env.reset(seed=seed + 100 + ep)
        done = False
        
        while not done:
            action_dict = {}
            for i in range(n_agents):
                if policy_type == "ma-rope" and coord is not None:
                    is_safety = (env.active_tasks[i]["type"] == "safety")
                    action_dict[i] = coord.agents[i].select_action(obs_dict[i], is_safety_task=is_safety, evaluate=True)
                else: # nooffload
                    action_dict[i] = 0
                    
            next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)
            done = dones_dict["__all__"] if "__all__" in dones_dict else list(dones_dict.values())[0]
            
            for i in range(n_agents):
                info = infos_dict[i]
                active_rng = np.random.RandomState(seed + ep * 1000 + env.episode_step * 10 + i)
                is_active = (active_rng.uniform(0.0, 1.0) < 0.3)
                
                if is_active:
                    metrics["u_prr"].append(rewards_dict[i])
                    metrics["u_otr"].append(info["u_otr"])
                    metrics["lat"].append(info["latency_ms"])
                    metrics["eng"].append(info["energy_j"])
                    
                    act = action_dict[i]
                    metrics["actions"][act] += 1
                    
                    from env.config import ACTION_MAP
                    rho = ACTION_MAP[act][1]
                    metrics["rhos"].append(rho)
                    metrics["total_decisions"] += 1
                    if rho == 0.0:
                        metrics["local_frac"] += 1
                    elif rho == 1.0:
                        metrics["full_frac"] += 1
                    else:
                        metrics["partial_frac"] += 1
                        
                    rsu_idx = env._get_nearest_rsu(env.positions[i])
                    metrics["queue_loss"].append(env.rsu_queues[rsu_idx])
                    
                if info["chosen_rat"] > 0 and info["chosen_rho"] > 0.0:
                    metrics["prr"].append(1.0 if info["transmission_success"] else 0.0)
                    metrics["fleet_otr"].append(1.0 if (info["transmission_success"] and info["latency_ms"] <= env.active_tasks[i]["D_ms"]) else 0.0)
            
            obs_dict = next_obs_dict
            
    return {
        "u_prr": np.mean(metrics["u_prr"]) if metrics["u_prr"] else 0.0,
        "u_otr": np.mean(metrics["u_otr"]) if metrics["u_otr"] else 0.0,
        "fleet_otr": np.mean(metrics["fleet_otr"]) if metrics["fleet_otr"] else 1.0,
        "prr": np.mean(metrics["prr"]) if metrics["prr"] else 1.0,
        "latency": np.mean(metrics["lat"]) if metrics["lat"] else 0.0,
        "energy": np.mean(metrics["eng"]) if metrics["eng"] else 0.0,
        "queue_loss": np.mean(metrics["queue_loss"]) if metrics["queue_loss"] else 0.0,
        "local_frac": metrics["local_frac"] / max(metrics["total_decisions"], 1),
        "partial_frac": metrics["partial_frac"] / max(metrics["total_decisions"], 1),
        "full_frac": metrics["full_frac"] / max(metrics["total_decisions"], 1),
        "actions": metrics["actions"],
        "mean_rho": np.mean(metrics["rhos"]) if metrics["rhos"] else 0.0
    }

def analyze_mode(mode):
    print(f"\n--- Analyzing Mode: {mode} ---")
    
    # 1. Exact local reward
    env = V2XEnv(n_vehicles=1, seed=42, mode="manuscript_calibrated", energy_mode="energy_si_corrected", local_reliability_mode=mode)
    
    tasks = {
        "safety": {"type": "safety", "D_ms": 100.0, "data_mb": 0.1, "cpu_cycles": 1e8, "alpha": 0.70, "beta": 0.30},
        "infotainment": {"type": "infotainment", "D_ms": 500.0, "data_mb": 2.0, "cpu_cycles": 5e8, "alpha": 0.40, "beta": 0.60},
        "compute": {"type": "compute", "D_ms": 1000.0, "data_mb": 5.0, "cpu_cycles": 2e9, "alpha": 0.20, "beta": 0.80}
    }
    
    print("\nLocal Rewards:")
    local_rews = {}
    for t_name, t_spec in tasks.items():
        env.reset()
        env.active_tasks[0] = t_spec
        # action 0 is NoOffload
        obs, rews, done, info = env.step({0: 0})
        print(f"  {t_name}: {rews[0]:.4f}")
        local_rews[t_name] = rews[0]

    # 2. Evaluate NoOffload
    res = custom_eval("manuscript_calibrated", "nooffload", 32, 42, episodes=10, energy_mode="energy_si_corrected", local_reliability_mode=mode)
    print("\nNoOffload Baseline:")
    print(f"  U_PRR: {res['u_prr']:.4f}, Energy: {res['energy']:.4f}, Latency: {res['latency']:.4f}")

    # 3. Train D3QN over 5 seeds
    print("\nTraining MA-ROPE over 5 seeds...")
    all_metrics = []
    
    for seed in range(5):
        print(f"  Training Seed {seed}...")
        
        # Train agent
        coord, ckpt_hash = train_ma_rope(
            env_mode="manuscript_calibrated",
            n_agents=32,
            seed=seed,
            episodes=100,
            energy_mode="energy_si_corrected",
            local_reliability_mode=mode
        )
        
        # Evaluate agent
        print(f"  Evaluating Seed {seed}...")
        res_rl = custom_eval(
            env_mode="manuscript_calibrated",
            policy_type="ma-rope",
            n_agents=32,
            seed=seed,
            coord=coord,
            episodes=5,
            energy_mode="energy_si_corrected",
            local_reliability_mode=mode
        )
        all_metrics.append(res_rl)
        
    # Aggregate RL metrics
    u_prr = np.mean([r["u_prr"] for r in all_metrics])
    u_otr = np.mean([r["u_otr"] for r in all_metrics])
    fleet_otr = np.mean([r["fleet_otr"] for r in all_metrics])
    lat = np.mean([r["latency"] for r in all_metrics])
    eng = np.mean([r["energy"] for r in all_metrics])
    q_loss = np.mean([r["queue_loss"] for r in all_metrics])
    l_frac = np.mean([r["local_frac"] for r in all_metrics])
    p_frac = np.mean([r["partial_frac"] for r in all_metrics])
    f_frac = np.mean([r["full_frac"] for r in all_metrics])
    m_rho = np.mean([r["mean_rho"] for r in all_metrics])
    
    print(f"\nRL Results (N=32) over 5 seeds:")
    print(f"  U_PRR: {u_prr:.4f}")
    print(f"  U_OTR: {u_otr:.4f}")
    print(f"  Fleet OTR: {fleet_otr:.4f}")
    print(f"  Latency: {lat:.4f} ms")
    print(f"  Energy: {eng:.4f} J")
    print(f"  Local/Partial/Full: {l_frac:.2f} / {p_frac:.2f} / {f_frac:.2f}")
    
    return {
        "mode": mode,
        "local_rewards": local_rews,
        "nooffload": res,
        "rl": {
            "u_prr": u_prr,
            "u_otr": u_otr,
            "fleet_otr": fleet_otr,
            "lat": lat,
            "eng": eng,
            "queue_loss": q_loss,
            "local_frac": l_frac,
            "partial_frac": p_frac,
            "full_frac": f_frac,
            "mean_rho": m_rho,
            "actions": {k: np.sum([r["actions"][k] for r in all_metrics]) for k in range(11)}
        }
    }

if __name__ == "__main__":
    results = {}
    for mode in MODES:
        results[mode] = analyze_mode(mode)
    
    os.makedirs("results/phase4a8", exist_ok=True)
    with open("results/phase4a8/aggregate.json", "w") as f:
        # Avoid non-serializable dict output for complex types like int64
        def convert(o):
            if isinstance(o, np.int64): return int(o)
            raise TypeError
        json.dump(results, f, indent=4, default=convert)
        
    print("\nPhase 4A.8 Evaluation Complete. Results saved to results/phase4a8/aggregate.json")
