import numpy as np
import json
import matplotlib.pyplot as plt
from env.environment_plus import V2XEnvPlus

def measure_workload(env, policy_name, num_slots=10000):
    # num_slots / 100 slots per episode = 100 episodes
    episodes = num_slots // 100
    
    offloaded_workloads = []
    
    for ep in range(episodes):
        obs = env.reset(seed=42 + ep)
        dones = {"__all__": False}
        
        while not dones["__all__"]:
            actions = {}
            for i in range(env.n_vehicles):
                is_safety = (obs[i][11] == 1.0)
                
                if policy_name == "random":
                    actions[i] = np.random.choice([0, 4, 5, 6, 7, 8, 9, 10]) if is_safety else np.random.choice(11)
                elif policy_name == "always_lte":
                    actions[i] = 4 if is_safety else 5
                elif policy_name == "always_5g":
                    actions[i] = 10
            
            obs, rewards, dones, infos = env.step(actions)
            
            # The environment executes the offloaded workload
            # In V2XEnvPlus, W_t_arr is the sum of tasks offloaded to the MEC server
            # We can calculate this by checking which tasks were offloaded
            w_arr = 0
            for i in range(env.n_vehicles):
                if infos[i]["has_task"]:
                    eff_act = infos[i]["effective_action"]
                    # If offloaded (eff_act > 0)
                    if eff_act > 0:
                        # Find task size L
                        L_i = obs[i][16] * 15e6
                        w_arr += L_i
                        
            offloaded_workloads.append(w_arr)
            
    return offloaded_workloads

def run_calibration():
    env = V2XEnvPlus(n_vehicles=16, seed=42)
    
    policies = ["random", "always_lte", "always_5g"]
    workload_data = {}
    
    print("Collecting workload statistics over 10,000 slots per policy...")
    for p in policies:
        print(f"Running {p}...")
        w_data = measure_workload(env, p, num_slots=10000)
        workload_data[p] = np.array(w_data)
        
    # Analyze Always 5G, as it gives the highest offloaded load (all tasks offloaded)
    baseline_w = workload_data["always_5g"]
    
    mean_w = np.mean(baseline_w)
    median_w = np.median(baseline_w)
    p75_w = np.percentile(baseline_w, 75)
    p90_w = np.percentile(baseline_w, 90)
    p95_w = np.percentile(baseline_w, 95)
    max_w = np.max(baseline_w)
    
    print("\n--- Workload Arrivals (Cycles/slot) for Always-5G ---")
    print(f"Mean:   {mean_w:,.0f}")
    print(f"Median: {median_w:,.0f}")
    print(f"P75:    {p75_w:,.0f}")
    print(f"P90:    {p90_w:,.0f}")
    print(f"P95:    {p95_w:,.0f}")
    print(f"Max:    {max_w:,.0f}")
    
    targets = [0.30, 0.50, 0.70, 0.80, 0.95, 1.05]
    dt = 0.1
    
    print(f"\n--- Target MEC Capacities (f_MEC) given dt={dt}s ---")
    capacities = {}
    for u in targets:
        # u = f_MEC * dt / mean_w
        # f_MEC = mean_w / (u * dt) ? Wait: u = (mean_w / dt) / f_MEC => f_MEC = mean_w / (u * dt)
        # Actually: f_MEC = mean_w / (u * dt)
        f_mec = mean_w / (u * dt)
        capacities[f"u_{u}"] = f_mec
        print(f"Target u={u:.2f} -> f_MEC = {f_mec/1e9:.3f} GHz")
        
    with open("load_calibration.json", "w") as f:
        json.dump({
            "always_5g_stats": {
                "mean": mean_w,
                "median": median_w,
                "p75": p75_w,
                "p90": p90_w,
                "p95": p95_w,
                "max": max_w
            },
            "capacities": capacities
        }, f, indent=4)
        
if __name__ == "__main__":
    run_calibration()
