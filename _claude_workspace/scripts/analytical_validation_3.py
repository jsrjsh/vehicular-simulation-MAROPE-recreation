import json
import math
import numpy as np
import random

TASKS = {
    "safety": {"D": 100.0, "data": 0.1, "cycles": 1e8, "alpha": 0.7, "beta": 0.3, "speedup": 1.5},
    "infotainment": {"D": 500.0, "data": 2.0, "cycles": 5e8, "alpha": 0.4, "beta": 0.6, "speedup": 1.0},
    "compute": {"D": 1000.0, "data": 5.0, "cycles": 2e9, "alpha": 0.2, "beta": 0.8, "speedup": 1.0}
}
RATS = {
    1: {"name": "LTE", "prop": 20.0, "tput": 50.0, "energy": 1.5},
    2: {"name": "ITS-G5", "prop": 10.0, "tput": 27.0, "energy": 2.0},
    3: {"name": "WiFi-6", "prop": 5.0, "tput": 600.0, "energy": 1.0},
    4: {"name": "5G", "prop": 1.0, "tput": 1000.0, "energy": 0.8}
}
REMOTE_BASE = 0.5e-3
P_CPU = 2.0

ACTIONS = {
    0: {"rat": 0, "rho": 0.0},
    1: {"rat": 1, "rho": 0.25}, 2: {"rat": 1, "rho": 0.50}, 3: {"rat": 1, "rho": 0.75}, 4: {"rat": 1, "rho": 1.0},
    5: {"rat": 2, "rho": 0.25}, 6: {"rat": 2, "rho": 0.50}, 7: {"rat": 2, "rho": 0.75}, 8: {"rat": 2, "rho": 1.0},
    9: {"rat": 3, "rho": 0.25}, 10: {"rat": 3, "rho": 0.50}, 11: {"rat": 3, "rho": 0.75}, 12: {"rat": 3, "rho": 1.0},
    13: {"rat": 4, "rho": 0.25}, 14: {"rat": 4, "rho": 0.50}, 15: {"rat": 4, "rho": 0.75}, 16: {"rat": 4, "rho": 1.0}
}

def simulate_action(task_name, action_idx, freq_hz, prr, rsu_load):
    task = TASKS[task_name]
    a = ACTIONS[action_idx]
    
    l_local_full = (task["cycles"] / freq_hz) * 1000.0
    
    if a["rho"] == 0.0:
        l_total = l_local_full
        e_total = P_CPU * (l_local_full / 1000.0)
    else:
        rat = RATS[a["rat"]]
        rho = a["rho"]
        
        l_loc_rho = l_local_full * (1.0 - rho)
        e_loc_rho = P_CPU * (l_loc_rho / 1000.0)
        
        l_prop = rat["prop"]
        l_tx = (task["data"] * rho * 8.0 / rat["tput"]) * 1000.0
        l_rem = (task["data"] * rho * (REMOTE_BASE / task["speedup"])) * 1000.0
        l_queue = rsu_load * 50.0
        
        l_offload = l_prop + l_tx + l_rem + l_queue
        l_total = max(l_loc_rho, l_offload)
        
        e_tx = (rat["energy"] * task["data"] * rho) / 1000.0
        e_total = e_loc_rho + e_tx

    l_ratio = max(min(l_total / task["D"], 100.0), -100.0)
    e_ratio = max(min(e_total / 3.0, 100.0), -100.0)
    
    success = (l_total <= task["D"])
    
    if a["rho"] == 0.0:
        actual_prr = 1.0
    else:
        actual_prr = prr
        
    u_success = task["alpha"] * 1.0 + (task["beta"] / 2) * math.exp(-l_ratio) + (task["beta"] / 2) * math.exp(-e_ratio)
    u_fail = task["alpha"] * 0.0 + (task["beta"] / 2) * 0.0 + (task["beta"] / 2) * math.exp(-e_ratio)
    
    expected_u = actual_prr * u_success + (1.0 - actual_prr) * u_fail
    
    return {
        "l_total": l_total,
        "e_total": e_total,
        "success": success,
        "reward": expected_u,
        "rat_idx": a["rat"],
        "rho": a["rho"],
        "rat_name": RATS[a["rat"]]["name"] if a["rat"]!=0 else "Local"
    }

def analyze_sweep(freq_hz):
    results = []
    
    prrs = [0.7, 0.8, 0.9, 1.0]
    rsu_loads = [0, 2, 4, 8, 12, 16]
    
    for t_name in TASKS:
        for prr in prrs:
            for rsu_load in rsu_loads:
                best_a = -1
                best_u = -1
                outcomes = {}
                for a in ACTIONS:
                    res = simulate_action(t_name, a, freq_hz, prr, rsu_load)
                    outcomes[a] = res
                    if res["reward"] > best_u:
                        best_u = res["reward"]
                        best_a = a
                
                cat = "Local"
                rho = ACTIONS[best_a]["rho"]
                if rho == 1.0: cat = "Full Offload"
                elif rho > 0.0: cat = "Partial Offload"
                
                results.append({
                    "task": t_name, "prr": prr, "rsu_load": rsu_load,
                    "best_rat": outcomes[best_a]["rat_name"],
                    "best_rho": rho,
                    "category": cat
                })
                
    stats = {"Local": 0, "Partial Offload": 0, "Full Offload": 0}
    rat_stats = {"Local": 0, "LTE": 0, "ITS-G5": 0, "WiFi-6": 0, "5G": 0}
    
    for r in results:
        stats[r["category"]] += 1
        rat_stats[r["best_rat"]] += 1
        
    for k in stats:
        stats[k] = stats[k] / len(results)
    for k in rat_stats:
        rat_stats[k] = rat_stats[k] / len(results)
        
    print(f"Stats for {freq_hz/1e9} GHz:")
    print("Categories:", stats)
    print("RATs:", rat_stats)
    print()

for f in [0.8e9, 1.0e9, 1.2e9, 1.5e9, 2.0e9]:
    analyze_sweep(f)
