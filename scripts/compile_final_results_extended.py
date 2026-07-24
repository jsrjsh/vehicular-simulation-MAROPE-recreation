import pandas as pd
import numpy as np
import os
import json
import matplotlib.pyplot as plt

MODES = ["shared", "independent", "fedavg"]
SEEDS = [42, 43, 44, 45, 46]
METRICS = ["success_rate", "reward", "latency_success", "energy", "queue"]

manifest = []

# --- 1. Run Integrity and Manifest ---
for mode in MODES:
    for seed in SEEDS:
        csv_path = f"results_{mode}_seed_{seed}.csv"
        checkpoint_path = f"checkpoints_{mode}/seed_{seed}_best.pt"
        
        has_csv = os.path.exists(csv_path)
        has_ckpt = os.path.exists(checkpoint_path)
        
        episodes_completed = 0
        if has_csv:
            try:
                df = pd.read_csv(csv_path)
                episodes_completed = df['episode'].max()
            except:
                pass
                
        manifest.append({
            "mode": mode,
            "seed": seed,
            "training_completed_successfully": bool(episodes_completed == 200),
            "episodes_completed": int(episodes_completed),
            "csv_written": bool(has_csv),
            "best_checkpoint_saved": bool(has_ckpt),
            "csv_path": csv_path,
            "checkpoint_path": checkpoint_path
        })

with open("experiment_manifest.json", "w") as f:
    json.dump(manifest, f, indent=4)


# --- 2. Compilation and Artifact Generation ---
results_md = "# Phase B3 Final Results (5-Seed Averaged)\n\n"

# Convergence Figure
results_md += "## Learning Convergence\n"
results_md += "![Learning Curves](/home/researcher/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/learning_curves.png)\n\n"

# Aggregated Statistics Table
results_md += "## Aggregated Statistical Report (Final Episode)\n"
results_md += "| Policy | Metric | Mean | Std | 95% CI | Min | Max |\n"
results_md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"

per_seed_data = []

plt.figure(figsize=(10, 6))

for mode in MODES:
    mode_metrics = {m: [] for m in METRICS}
    
    # For plotting
    all_rewards = []
    episodes = None
    
    for seed in SEEDS:
        csv_file = f"results_{mode}_seed_{seed}.csv"
        if not os.path.exists(csv_file):
            continue
            
        df = pd.read_csv(csv_file)
        final_row = df.iloc[-1]
        
        if episodes is None:
            episodes = df['episode'].values
        all_rewards.append(df['reward'].values)
        
        for m in METRICS:
            mode_metrics[m].append(final_row[m])
            
        per_seed_data.append({
            "Seed": seed,
            "Policy": mode.capitalize(),
            "Reward": final_row["reward"],
            "Success Rate": final_row["success_rate"],
            "Latency (ms)": final_row["latency_success"] * 1000,
            "Energy (mJ)": final_row["energy"] * 1000
        })
            
    # Compute and format stats
    for m in METRICS:
        data = mode_metrics[m]
        if not data:
            continue
            
        mean = np.mean(data)
        std = np.std(data, ddof=1) if len(data) > 1 else 0.0
        std_err = std / np.sqrt(len(data))
        margin = 2.776 * std_err if len(data) > 1 else 0.0
        min_val = np.min(data)
        max_val = np.max(data)
        
        if m in ["latency_success", "energy"]:
            mean *= 1000
            std *= 1000
            margin *= 1000
            min_val *= 1000
            max_val *= 1000
            
        if m == "success_rate":
            mean_str = f"{mean*100:.2f}%"
            std_str = f"{std*100:.2f}%"
            ci_str = f"± {margin*100:.2f}%"
            min_str = f"{min_val*100:.2f}%"
            max_str = f"{max_val*100:.2f}%"
        else:
            mean_str = f"{mean:.3f}"
            std_str = f"{std:.3f}"
            ci_str = f"± {margin:.3f}"
            min_str = f"{min_val:.3f}"
            max_str = f"{max_val:.3f}"
            
        # Only print mode name on the first row (reward)
        mode_label = f"**{mode.capitalize()}**" if m == METRICS[0] else ""
        results_md += f"| {mode_label} | {m} | {mean_str} | {std_str} | {ci_str} | {min_str} | {max_str} |\n"
        
    # Add to plot
    if all_rewards:
        rewards_arr = np.array(all_rewards)
        mean_rewards = np.mean(rewards_arr, axis=0)
        std_rewards = np.std(rewards_arr, axis=0, ddof=1)
        ci_rewards = 2.776 * (std_rewards / np.sqrt(len(SEEDS)))
        
        plt.plot(episodes, mean_rewards, label=mode.capitalize())
        plt.fill_between(episodes, mean_rewards - ci_rewards, mean_rewards + ci_rewards, alpha=0.2)

# Save plot
plt.title('Learning Convergence (Reward vs Episode)')
plt.xlabel('Episodes')
plt.ylabel('Mean Reward')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/home/researcher/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/learning_curves.png', dpi=150)
plt.close()

# --- 3. Per-Seed Results Table ---
results_md += "\n## Per-Seed Results\n"
results_md += "| Policy | Seed | Reward | Success Rate | Latency (ms) | Energy (mJ) |\n"
results_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
for row in sorted(per_seed_data, key=lambda x: (x["Policy"], x["Seed"])):
    results_md += f"| {row['Policy']} | {row['Seed']} | {row['Reward']:.3f} | {row['Success Rate']*100:.1f}% | {row['Latency (ms)']:.1f} | {row['Energy (mJ)']:.3f} |\n"

# Output to artifact path
artifact_path = "/home/researcher/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/PHASE_B3_FINAL_RESULTS.md"
with open(artifact_path, "w") as f:
    f.write(results_md)
    
print("Successfully generated final results artifact and plot.")
