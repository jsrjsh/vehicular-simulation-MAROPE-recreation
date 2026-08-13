import pandas as pd
import numpy as np
import glob
import os

MODES = ["shared", "independent", "fedavg"]
SEEDS = [42, 43, 44, 45, 46]
METRICS = ["success_rate", "reward", "latency_success", "energy", "queue"]

results_md = "# Phase B3 Final Results (5-Seed Averaged)\n\n"
results_md += "| Policy | Success Rate | Reward | Latency (ms) | Energy (mJ) | Queue Backlog |\n"
results_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

for mode in MODES:
    mode_metrics = {m: [] for m in METRICS}
    
    for seed in SEEDS:
        csv_file = f"results_{mode}_seed_{seed}.csv"
        if not os.path.exists(csv_file):
            print(f"Warning: {csv_file} not found.")
            continue
            
        df = pd.read_csv(csv_file)
        # Take the final evaluation (episode 200)
        final_row = df.iloc[-1]
        
        for m in METRICS:
            mode_metrics[m].append(final_row[m])
            
    # Compute mean and 95% CI
    stats_str = {}
    for m in METRICS:
        data = mode_metrics[m]
        mean = np.mean(data)
        std_err = np.std(data, ddof=1) / np.sqrt(len(data))
        # 95% CI using Student's t distribution with 4 dof (t_0.025, 4 = 2.776)
        margin = 2.776 * std_err if len(data) > 1 else 0.0
        
        if m in ["latency_success", "energy"]:
            # Convert to ms and mJ
            mean *= 1000
            margin *= 1000
            
        if m == "success_rate":
            stats_str[m] = f"{mean*100:.1f}% ± {margin*100:.1f}%"
        elif m in ["queue"]:
            stats_str[m] = f"{mean:.1f} ± {margin:.1f}"
        else:
            stats_str[m] = f"{mean:.3f} ± {margin:.3f}"
            
    results_md += f"| **{mode.capitalize()}** | {stats_str['success_rate']} | {stats_str['reward']} | {stats_str['latency_success']} | {stats_str['energy']} | {stats_str['queue']} |\n"

# Output to artifact path
artifact_path = "/home/researcher/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/PHASE_B3_FINAL_RESULTS.md"
with open(artifact_path, "w") as f:
    f.write(results_md)
    
print("Successfully generated final results artifact.")
