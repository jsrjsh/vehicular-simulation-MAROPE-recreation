import pandas as pd
import numpy as np
import sys
import os
import datetime

# Add _claude_workspace to path so env modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from env.channel import compute_sinr, compute_link_success

def get_analytical_prob(rat_idx, dist, speed, n_samples=100, rng=None):
    if rng is None:
        rng = np.random.RandomState()
    successes = 0
    for _ in range(n_samples):
        sinr = compute_sinr(rat_idx, dist, speed, rng, mode="physically_corrected")
        if compute_link_success(rat_idx, sinr, rng, mode="physically_corrected"):
            successes += 1
    return successes / n_samples

def main(csv_file, output_report_dir):
    print(f"Loading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Filter for SUCCESS or TIMEOUT (actual network transmission outcomes)
    df = df[df['Status'].isin(['SUCCESS', 'TIMEOUT'])].copy()
    
    # Map decision to RAT idx
    # MEC -> WiFi-6 (idx=3), CLOUD -> LTE (idx=1)
    df['rat_idx'] = df['Decision'].map({'MEC': 3, 'CLOUD': 1})
    
    # Convert success bool
    df['Empirical_Success'] = (df['Status'] == 'SUCCESS').astype(int)
    
    rng = np.random.RandomState(42)
    
    print("Computing analytical probabilities...")
    df['Analytical_Prob'] = df.apply(
        lambda row: get_analytical_prob(row['rat_idx'], row['Distance'], row['Speed'], 100, rng), 
        axis=1
    )
    
    # Bin distances (50m bins up to 3000m)
    bins = np.arange(0, 3050, 50)
    labels = bins[:-1] + 25 # Bin centers
    df['DistBin'] = pd.cut(df['Distance'], bins=bins, labels=labels)
    
    os.makedirs(output_report_dir, exist_ok=True)
    report_path = os.path.join(output_report_dir, "SUMO_NS3_CHANNEL_VALIDATION_REPORT.md")
    
    with open(report_path, "w") as f:
        f.write("# SUMO vs ns-3 Channel Model Validation Report\n\n")
        f.write("This report validates the analytical `env/channel.py` physical layer model against an ns-3.41 simulation containing WiFi-6 (MEC) and LTE (CLOUD) modules.\n\n")
        f.write("## Module Setup\n")
        f.write("> [!NOTE]\n> Option (B) was selected: ITS-G5 and 5G-NR are currently deferred as the `wave` and `5G-LENA` modules are not installed in the current ns-3 tree.\n\n")
        
        f.write("## Provenance\n")
        f.write(f"- **Execution Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("- **ns-3 modules**: core, network, mobility, internet, wifi, lte, propagation\n")
        f.write("- **Run command**: `./ns3 run \"scratch/channel-validation --strategy=1 --traceFile=../mobility.tcl --csvFile=../simulation_results_channel_validation.csv\"`\n")
        f.write(f"- **Raw CSV paths**: `{os.path.abspath(csv_file)}`\n")
        f.write(f"- **Comparison script**: `{os.path.abspath(__file__)}`\n\n")
        
        for rat, rat_name in [(1, 'LTE (CLOUD)'), (3, 'WiFi-6 (MEC)')]:
            rat_df = df[df['rat_idx'] == rat]
            if len(rat_df) == 0:
                f.write(f"## {rat_name}\nNo transmissions recorded.\n\n")
                continue
            
            binned = rat_df.groupby('DistBin', observed=False).agg(
                Empirical_Prob=('Empirical_Success', 'mean'),
                Analytical_Prob=('Analytical_Prob', 'mean'),
                Count=('Status', 'count')
            ).reset_index()
            
            binned = binned[binned['Count'] > 0]
            if len(binned) == 0:
                continue
                
            binned['Divergence'] = (binned['Empirical_Prob'] - binned['Analytical_Prob']).abs()
            mean_divergence = binned['Divergence'].mean()
            
            f.write(f"## RAT: {rat_name}\n")
            f.write(f"**Mean Divergence (MAE across distance bins)**: {mean_divergence:.4f}\n\n")
            f.write("| Distance (m) | Count | Empirical Prob | Analytical Prob | Divergence |\n")
            f.write("|---|---|---|---|---|\n")
            for _, row in binned.iterrows():
                f.write(f"| {row['DistBin']:.1f} | {row['Count']:.0f} | {row['Empirical_Prob']:.4f} | {row['Analytical_Prob']:.4f} | {row['Divergence']:.4f} |\n")
            f.write("\n")
            
    print(f"Validation report generated at: {report_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validate_ns3_channel.py <csv_file> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
