import os
import sys
import numpy as np
import pandas as pd
import ast

def empirical_reward_audit():
    # We will compute the average components from the logs. Wait, the logs don't save the raw reward components!
    # They save reward, success_rate, latency, energy, queue.
    # We need to compute it offline using the env step!
    pass

def run_counterfactual_analysis():
    sys.path.append('.')
    from env.environment_plus import V2XEnvPlus
    
    env = V2XEnvPlus(n_vehicles=1, seed=123, f_mec=0.316e9, bg_workload_enabled=True)
    
    # State Strata
    queues = [0, 50e6, 90e6] # Low, Med, High
    task_classes = [1, 2, 3]
    distances = [10, 500, 1000] # dist from RSU (center 1300) -> pos = 1310, 1800, 2300
    
    results = []
    
    for q in queues:
        for tc in task_classes:
            for dist in distances:
                env.reset(seed=42)
                env.Q_t = q
                env.vehicles[0]["pos"] = 1300 + dist
                
                # Mock task
                if tc == 1:
                    task = {"class": 1, "D": 0.1, "B": 2400, "L": 1e6}
                elif tc == 2:
                    task = {"class": 2, "D": 0.5, "B": 10 * 8 * 1024, "L": 5e6}
                else:
                    task = {"class": 3, "D": 1.0, "B": 50 * 8 * 1024, "L": 15e6}
                    
                env.active_tasks[0] = task
                
                for a in range(11):
                    # Save state
                    env_state = {
                        "Q_t": env.Q_t,
                        "batt": env.vehicles[0]["battery"],
                        "pos": env.vehicles[0]["pos"]
                    }
                    
                    obs, rewards, dones, infos = env.step({0: a})
                    
                    # Extract
                    info = infos[0]
                    results.append({
                        "Queue": q,
                        "TaskClass": tc,
                        "Distance": dist,
                        "Action": a,
                        "ActionName": env.action_map[a][0],
                        "Rho": env.action_map[a][1],
                        "Success": info["S_i"],
                        "Latency": info["T_i"],
                        "Energy": info["E_i"],
                        "Reward": rewards[0]
                    })
                    
                    # Restore state
                    env.Q_t = env_state["Q_t"]
                    env.vehicles[0]["battery"] = env_state["batt"]
                    env.vehicles[0]["pos"] = env_state["pos"]
                    env.episode_step -= 1
                    env.active_tasks[0] = task
                    
    df = pd.DataFrame(results)
    df.to_csv("counterfactual_results.csv", index=False)
    print("Counterfactual evaluation complete. Saved to counterfactual_results.csv")

if __name__ == "__main__":
    os.makedirs("analysis", exist_ok=True)
    os.chdir("analysis")
    run_counterfactual_analysis()
