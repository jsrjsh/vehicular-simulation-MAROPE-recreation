import pandas as pd
import numpy as np

def analyze_b33f():
    df = pd.read_csv("analysis/B33F_TRAJECTORY_Q_VALUES.csv")
    
    print("--- 1. Queue Stratification ---")
    bins = [-1, 30e6, 40e6, 50e6, 70e6, 200e6]
    labels = ["<30M", "30-40M", "40-50M", "50-70M", ">=70M"]
    df["Queue_Stratum"] = pd.cut(df["Queue"], bins=bins, labels=labels)
    
    summary = []
    
    for stratum in labels:
        s_df = df[df["Queue_Stratum"] == stratum]
        n_states = len(s_df)
        if n_states == 0:
            continue
            
        pct_local_beats_5g = s_df["Local_beats_5G"].mean() * 100
        pct_local_argmax = s_df["Local_is_Argmax"].mean() * 100
        mean_delta = s_df["DeltaQ_5G_Loc"].mean()
        min_delta = s_df["DeltaQ_5G_Loc"].min()
        pct_lte_beats_5g = s_df["LTE_beats_5G"].mean() * 100
        
        act_dist = s_df["Argmax_Action"].value_counts(normalize=True)
        top_actions = {a: round(pct * 100, 1) for a, pct in act_dist.items() if pct > 0.05}
        
        summary.append({
            "Stratum": stratum,
            "N_States": n_states,
            "%_Local>5G": f"{pct_local_beats_5g:.2f}%",
            "%_Local=Argmax": f"{pct_local_argmax:.2f}%",
            "Mean_Delta": round(mean_delta, 3),
            "Min_Delta": round(min_delta, 3),
            "%_LTE>5G": f"{pct_lte_beats_5g:.2f}%",
            "Top_Actions": top_actions
        })
        
    for res in summary:
        print(f"\nStratum: {res['Stratum']} (N={res['N_States']})")
        print(f"  Local beats 5G: {res['%_Local>5G']}")
        print(f"  Local is Argmax: {res['%_Local=Argmax']}")
        print(f"  LTE beats 5G: {res['%_LTE>5G']}")
        print(f"  Delta(5G - Local): Mean {res['Mean_Delta']}, Min {res['Min_Delta']}")
        print(f"  Selected Actions: {res['Top_Actions']}")
        
    print("\n--- 2. Conclusion Mapping ---")
    high_q = df[df["Queue"] >= 50e6]
    if len(high_q) > 0:
        if high_q["Local_beats_5G"].mean() < 0.05:
            print("Outcome E1: High queue, but Local still loses to 5G. The joint-state distribution encountered during trajectories never falls in the Local-advantage region.")
        elif high_q["Local_beats_5G"].mean() > 0.5 and high_q["Local_is_Argmax"].mean() < 0.1:
            print("Outcome E2: Local beats 5G, but another action (e.g. LTE) wins the argmax.")
        elif high_q["Local_is_Argmax"].mean() > 0.5:
            print("Outcome E3: Local is Argmax, yet B3.3E reported 100% 5G. Evaluation/Logging inconsistency.")
        else:
            print("Mixed Outcome: Some states cross the boundary, some don't. Check distribution.")
    else:
        print("No states > 50M reached. Cannot classify.")
        
if __name__ == "__main__":
    analyze_b33f()
