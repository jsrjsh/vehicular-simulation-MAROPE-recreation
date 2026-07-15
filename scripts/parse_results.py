# scripts/parse_results.py
import os
import glob
import csv
import numpy as np

def parse():
    for n in [8, 32]:
        print(f"\n================ N = {n} ================")
        for mode in ["paper_reproduction", "physically_corrected"]:
            print(f"\n--- Environment Mode: {mode} ---")
            for policy in ["ma-rope", "alloffload", "nooffload"]:
                files = glob.glob(f"results/{mode}/n{n}/{policy}_seed_*_ep_5_hash_*.csv")
                
                # Filter out files
                data = {
                    "u_prr_active": [],
                    "u_otr_active": [],
                    "fleet_otr": [],
                    "prr": [],
                    "latency_active_ms": [],
                    "energy_active_j": [],
                    "queue_loss": []
                }
                
                for f in files:
                    if os.path.exists(f) and os.path.getsize(f) > 100:
                        with open(f, "r") as csvfile:
                            reader = csv.DictReader(csvfile)
                            for row in reader:
                                data["u_prr_active"].append(float(row["u_prr_active"]))
                                data["u_otr_active"].append(float(row["u_otr_active"]))
                                data["fleet_otr"].append(float(row["fleet_otr"]))
                                data["prr"].append(float(row["prr"]))
                                data["latency_active_ms"].append(float(row["latency_active_ms"]))
                                data["energy_active_j"].append(float(row["energy_active_j"]))
                                data["queue_loss"].append(float(row["queue_loss"]))
                                
                if not data["u_prr_active"]:
                    # Try fallback naming pattern
                    fallback_files = glob.glob(f"results/{mode}/n{n}/{policy}_seed_*.csv")
                    for f in fallback_files:
                        if os.path.exists(f) and os.path.getsize(f) > 100:
                            with open(f, "r") as csvfile:
                                reader = csv.DictReader(csvfile)
                                for row in reader:
                                    data["u_prr_active"].append(float(row["u_prr_active"]))
                                    data["u_otr_active"].append(float(row["u_otr_active"]))
                                    data["fleet_otr"].append(float(row["fleet_otr"]))
                                    data["prr"].append(float(row["prr"]))
                                    data["latency_active_ms"].append(float(row["latency_active_ms"]))
                                    data["energy_active_j"].append(float(row["energy_active_j"]))
                                    data["queue_loss"].append(float(row["queue_loss"]))
                
                if not data["u_prr_active"]:
                    print(f"Policy {policy}: No data found.")
                    continue
                
                print(f"Policy: {policy.upper()}")
                for col in ["u_prr_active", "u_otr_active", "fleet_otr", "prr", "latency_active_ms", "energy_active_j", "queue_loss"]:
                    vals = data[col]
                    mean_val = np.mean(vals)
                    std_val = np.std(vals)
                    print(f"  {col}: {mean_val:.4f} ± {std_val:.4f}")

if __name__ == "__main__":
    parse()
