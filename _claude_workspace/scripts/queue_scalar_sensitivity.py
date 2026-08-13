import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env.environment import V2XEnv

def evaluate_fixed_policy(policy, N, delay_scalar, mode="manuscript_calibrated", episodes=20):
    env = V2XEnv(n_vehicles=N, mode=mode, policy_type=policy, delay_per_unit_ms=delay_scalar)
    
    total_latency = 0.0
    total_u = 0.0
    total_u_otr = 0.0
    total_energy = 0.0
    total_active = 0
    total_tx = 0
    total_tx_success = 0
    total_tx_on_time = 0
    total_queue_delay = 0.0
    
    for ep in range(episodes):
        obs = env.reset(seed=42 + ep)
        done = False
        while not done:
            action_dict = {i: 8 if policy == "alloffload" else 0 for i in range(N)}
            next_obs, rewards, dones, infos = env.step(action_dict)
            done = dones["__all__"]
            
            active_rng = np.random.RandomState(42 + ep * 1000 + env.episode_step * 10)
            
            for i in range(N):
                is_active = (active_rng.uniform(0.0, 1.0) < 0.3)
                if is_active:
                    total_active += 1
                    total_u += rewards[i]
                    
                    info = infos[i]
                    total_latency += info["latency_ms"]
                    total_energy += info["energy_j"]
                    total_queue_delay += info.get("queue_delay_ms", 0.0)
                    total_u_otr += info["u_otr"]
                    
                    if info["chosen_rat"] > 0 and info["adapted_rho"] > 0.0:
                        total_tx += 1
                        if info["transmission_success"]:
                            total_tx_success += 1
                            if info["latency_ms"] <= env.active_tasks[i]["D_ms"]:
                                total_tx_on_time += 1
                    else:
                        if info["latency_ms"] <= env.active_tasks[i]["D_ms"]:
                            total_tx_on_time += 1
                            
    if total_active == 0:
        return {}
        
    avg_latency = total_latency / total_active
    avg_u = total_u / total_active
    avg_u_otr = total_u_otr / total_active
    avg_energy = total_energy / total_active
    avg_queue_delay = total_queue_delay / total_active
    fleet_otr = total_tx_on_time / total_tx if total_tx > 0 else (total_tx_on_time / total_active if policy == "nooffload" else 0.0)
    prr = total_tx_success / total_tx if total_tx > 0 else 1.0
    
    return {
        "latency": avg_latency,
        "u_prr": avg_u,
        "u_otr": avg_u_otr,
        "fleet_otr": fleet_otr,
        "energy": avg_energy,
        "queue_loss": avg_queue_delay,
        "prr": prr
    }

def main():
    delay_scalars = [25, 30, 32.5, 35, 37.5, 40, 45, 50]
    policies = ["alloffload", "nooffload"]
    fleet_sizes = [8, 32]
    
    with open("QUEUE_SCALAR_SENSITIVITY.md", "w") as f:
        f.write("# QUEUE SCALAR SENSITIVITY SWEEP\n\n")
        f.write("Fixed-policy evaluation across DELAY_PER_UNIT_MS in {25, ..., 50}.\n\n")
        
        for N in fleet_sizes:
            f.write(f"## Fleet Size N={N}\n\n")
            for policy in policies:
                f.write(f"### Policy: {policy.upper()}\n")
                f.write("| Scalar (ms) | U_PRR | U_OTR | Fleet OTR | Latency (ms) | Energy (J) | Queue Loss (ms) | PRR |\n")
                f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
                for scalar in delay_scalars:
                    res = evaluate_fixed_policy(policy, N, scalar, episodes=20)
                    f.write(f"| {scalar} | {res['u_prr']:.4f} | {res['u_otr']:.4f} | {res['fleet_otr']:.4f} | {res['latency']:.4f} | {res['energy']:.4f} | {res['queue_loss']:.4f} | {res['prr']:.4f} |\n")
                    f.flush()
                f.write("\n")

if __name__ == "__main__":
    main()
