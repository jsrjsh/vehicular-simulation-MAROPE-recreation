import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# IEEE standard style configuration
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.labelsize": 10,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.figsize": (3.5, 2.5), # Standard single column IEEE
    "figure.dpi": 300,
    "savefig.bbox": "tight"
})

output_dir = "paper/figures"
os.makedirs(output_dir, exist_ok=True)

# 2. Q-value Margins (Representation Probes)
def plot_q_value_margins():
    try:
        df = pd.read_csv("analysis/QUEUE_SENSITIVITY_RAW.csv")
    except FileNotFoundError:
        print("Missing QUEUE_SENSITIVITY_RAW.csv")
        return
        
    plt.figure()
    
    # We will just plot a few examples if there are many, or just plot all of them transparently
    for model in df['ModelPath'].unique():
        model_data = df[df['ModelPath'] == model].sort_values('Queue')
        plt.plot(model_data['Queue'] / 1e6, model_data['DeltaQ_5G_Loc'], 
                 alpha=0.5)
                 
    plt.axhline(0, color='red', linestyle='--', alpha=0.8, label='Action Inversion')
    plt.xlabel('5G Edge Queue (Millions of Cycles)')
    plt.ylabel(r'$\Delta Q_{5G-L}$ (Value Margin)')
    plt.title('Counterfactual Queue Sensitivity (FedAvg)')
    
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'fig_q_margins.pdf'))
    plt.close()

# 3. Decision Surface vs Occupancy
def plot_decision_surface():
    try:
        df = pd.read_csv("analysis/B33F_TRAJECTORY_Q_VALUES.csv")
    except FileNotFoundError:
        print("Missing B33F_TRAJECTORY_Q_VALUES.csv")
        return
        
    seeds = sorted(df['Seed'].unique())
    fig, axes = plt.subplots(1, len(seeds), figsize=(7, 2.5), sharey=True)
    
    for i, seed in enumerate(seeds):
        seed_data = df[df['Seed'] == seed]
        queues = seed_data['Queue'] / 1e6
        
        # Calculate Local action boundary
        local_mask = seed_data['Argmax_Action'] == 10
        if local_mask.any():
            min_local_queue = queues[local_mask].min()
        else:
            min_local_queue = 100 # effectively infinity
            
        axes[i].hist(queues, bins=50, color='gray', alpha=0.6, density=True)
        if min_local_queue < 100:
            axes[i].axvline(min_local_queue, color='red', linestyle='--', label=r'Learned $Q_{switch}$')
            axes[i].axvspan(min_local_queue, 100, color='red', alpha=0.1, label='Local Action Region')
        
        axes[i].set_title(f'Seed {seed}')
        axes[i].set_xlabel('5G Queue Occupancy (M cycles)')
        axes[i].set_xlim(0, 50)
        
    axes[0].set_ylabel('Empirical Density')
    handles, labels = axes[0].get_legend_handles_labels()
    if not handles:
        handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_decision_surface.pdf'), bbox_inches='tight')
    plt.close()

# 4. Matched Outcomes (Response Curves)
def plot_matched_outcomes():
    try:
        df = pd.read_csv("analysis/B33F_MATCHED_OUTCOMES.csv")
    except FileNotFoundError:
        print("Missing B33F_MATCHED_OUTCOMES.csv")
        return
        
    seeds = sorted(df['Seed'].unique())
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.5))
    
    colors = {111: '#1f77b4', 222: '#ff7f0e', 333: '#2ca02c'}
    markers = {111: 'o', 222: 's', 333: '^'}
    
    for seed in seeds:
        seed_data = df[df['Seed'] == seed].sort_values('p_task')
        x = seed_data['p_task']
        
        # SLA
        axes[0].plot(x, seed_data['SLA_Success'], label=f'Seed {seed}', 
                     color=colors[seed], marker=markers[seed])
                     
        # p95 Queue
        axes[1].plot(x, seed_data['p95_Queue'] / 1e6, label=f'Seed {seed}',
                     color=colors[seed], marker=markers[seed])
                     
    axes[0].set_ylabel('SLA Success Rate (%)')
    axes[0].set_xlabel(r'Task Arrival Probability ($p_{task}$)')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    
    axes[1].set_ylabel('p95 Queue (M cycles)')
    axes[1].set_xlabel(r'Task Arrival Probability ($p_{task}$)')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_matched_outcomes.pdf'))
    plt.close()

if __name__ == "__main__":
    plot_q_value_margins()
    plot_decision_surface()
    plot_matched_outcomes()
    print("Figures generated in paper/figures/")
