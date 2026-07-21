import pandas as pd
import numpy as np
import os
import json
import matplotlib.pyplot as plt
import re

MODES = ["shared", "independent", "fedavg"]
SEEDS = [42, 43, 44, 45, 46]
METRICS = ["success_rate", "reward", "latency_success", "energy", "queue", "div_before", "div_after", "success_disp", "reward_disp"]

# Convergence Figure
results_md = "# Phase B3 Final Results (5-Seed Averaged)\n\n"
results_md += "## Learning Convergence\n"
results_md += "![Learning Curves](/Users/aryaveersingh/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/learning_curves.png)\n\n"

# Aggregated Statistics Table
results_md += "## Aggregated Statistical Report (Final Episode)\n"
results_md += "| Policy | Metric | Mean | Std | 95% CI | Min | Max |\n"
results_md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"

per_seed_data = []
plt.figure(figsize=(10, 6))

for mode in MODES:
    mode_metrics = {m: [] for m in METRICS}
    mode_action_dist = {"L": [], "LTE": [], "5G": []}
    
    # For plotting
    all_rewards = []
    episodes = None
    
    for seed in SEEDS:
        csv_file = f"results_{mode}_seed_{seed}.csv"
        log_file = f"logs_{mode}_seed_{seed}.txt"
        
        if not os.path.exists(csv_file):
            continue
            
        df = pd.read_csv(csv_file)
        df = df.drop_duplicates(subset=['episode'], keep='last')
        df = df.sort_values('episode')
        final_row = df.iloc[-1]
        
        if episodes is None:
            episodes = df['episode'].values
        all_rewards.append(df['reward'].values)
        
        for m in METRICS:
            if m in final_row:
                mode_metrics[m].append(final_row[m])
                
        # Parse action distribution from logs
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                content = f.read()
                # Find the last occurrence of Act Dist
                matches = re.findall(r"Act Dist: L=([0-9.]+), LTE=([0-9.]+), 5G=([0-9.]+)", content)
                if matches:
                    last_match = matches[-1]
                    mode_action_dist["L"].append(float(last_match[0]))
                    mode_action_dist["LTE"].append(float(last_match[1]))
                    mode_action_dist["5G"].append(float(last_match[2]))
        
        # Determine L/LTE/5G actions for this seed
        a_l, a_lte, a_5g = 0.0, 0.0, 0.0
        if len(mode_action_dist["L"]) > 0:
            a_l = mode_action_dist["L"][-1]
            a_lte = mode_action_dist["LTE"][-1]
            a_5g = mode_action_dist["5G"][-1]

        per_seed_data.append({
            "Seed": seed,
            "Policy": mode.capitalize(),
            "Reward": final_row["reward"],
            "Success Rate": final_row["success_rate"],
            "Latency (ms)": final_row["latency_success"] * 1000,
            "Energy (mJ)": final_row["energy"] * 1000,
            "Reward Disp": final_row.get("reward_disp", 0.0),
            "Div Before": final_row.get("div_before", 0.0),
            "L%": a_l * 100,
            "LTE%": a_lte * 100,
            "5G%": a_5g * 100
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
            
        if m in ["success_rate", "eligible_fraction"]:
            mean_str = f"{mean*100:.2f}%"
            std_str = f"{std*100:.2f}%"
            ci_str = f"± {margin*100:.2f}%"
            min_str = f"{min_val*100:.2f}%"
            max_str = f"{max_val*100:.2f}%"
        else:
            mean_str = f"{mean:.4f}"
            std_str = f"{std:.4f}"
            ci_str = f"± {margin:.4f}"
            min_str = f"{min_val:.4f}"
            max_str = f"{max_val:.4f}"
            
        mode_label = f"**{mode.capitalize()}**" if m == METRICS[0] else ""
        results_md += f"| {mode_label} | {m} | {mean_str} | {std_str} | {ci_str} | {min_str} | {max_str} |\n"
        
    # Append action dist stats
    if len(mode_action_dist["L"]) > 0:
        for a in ["L", "LTE", "5G"]:
            data = mode_action_dist[a]
            mean = np.mean(data)
            std = np.std(data, ddof=1) if len(data) > 1 else 0.0
            std_err = std / np.sqrt(len(data))
            margin = 2.776 * std_err if len(data) > 1 else 0.0
            
            results_md += f"| | Action % ({a}) | {mean*100:.1f}% | {std*100:.1f}% | ± {margin*100:.1f}% | {np.min(data)*100:.1f}% | {np.max(data)*100:.1f}% |\n"

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
plt.savefig('/Users/aryaveersingh/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/learning_curves.png', dpi=150)
plt.close()

# --- 3. Per-Seed Results Table ---
results_md += "\n## Per-Seed Results\n"
results_md += "| Policy | Seed | Reward | Success | Latency (ms) | Energy (mJ) | Rwd Disp | Div Before | L / LTE / 5G % |\n"
results_md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
for row in sorted(per_seed_data, key=lambda x: (x["Policy"], x["Seed"])):
    actions_str = f"{row['L%']:.0f} / {row['LTE%']:.0f} / {row['5G%']:.0f}"
    div_str = f"{row['Div Before']:.3f}" if row['Div Before'] > 0 else "-"
    results_md += f"| {row['Policy']} | {row['Seed']} | {row['Reward']:.3f} | {row['Success Rate']*100:.1f}% | {row['Latency (ms)']:.1f} | {row['Energy (mJ)']:.3f} | {row['Reward Disp']:.3f} | {div_str} | {actions_str} |\n"

# Output to artifact path
artifact_path = "/Users/aryaveersingh/.gemini/antigravity-ide/brain/534992f3-aa80-47de-bf35-190f84414b21/PHASE_B3_FINAL_RESULTS.md"
with open(artifact_path, "w") as f:
    f.write(results_md)
    
print("Successfully updated final results artifact.")
