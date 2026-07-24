import pandas as pd

print("--- Data Integrity ---")
df_pilot = pd.read_csv("analysis/stage2_pilot_results.csv")
print("Total Pilot Runs:", len(df_pilot))
print(df_pilot.groupby(["Mode", "Config"]).size())

print("\n--- B3.3B Behavioral Results ---")
print(df_pilot.groupby(["Mode", "Config"])[["5G_Ratio", "SLA_Success", "Energy", "Latency_ms"]].mean())

print("\n--- B3.3C Representation Results ---")
df_qs = pd.read_csv("analysis/QUEUE_SENSITIVITY_RAW.csv")
print("Total probes evaluated:", len(df_qs))

# We want to see DeltaQ_5G_Loc for Q=0 and Q=100M
q_low = df_qs[df_qs["Queue"] == 0.0].copy()
q_high = df_qs[df_qs["Queue"] == 100e6].copy()

# Merge to compute S_Q
m = pd.merge(q_low, q_high, on=["ModelPath", "ClientIdx", "Scenario", "SupportType"], suffixes=("_low", "_high"))
m["S_Q"] = m["DeltaQ_5G_Loc_low"] - m["DeltaQ_5G_Loc_high"]

# Parse Mode and Config from ModelPath
m["Mode"] = m["ModelPath"].apply(lambda x: x.split("/")[1].split("_")[0])
m["Config"] = m["ModelPath"].apply(lambda x: "Candidate_" + x.split("/")[1].split("_")[2] if "Candidate" in x else "Baseline")

res = m.groupby(["Mode", "Config"])["S_Q"].mean().reset_index()
print("\nMean Queue Sensitivity Score (S_Q) by Mode/Config (averaged over clients and scenarios):")
print(res)

print("\nFraction of scenarios with S_Q > 0 (positive queue sensitivity):")
m["positive_sq"] = m["S_Q"] > 0
print(m.groupby(["Mode", "Config"])["positive_sq"].mean())

print("\nAction selections at Low Queue:")
print(q_low["Action"].value_counts(normalize=True))
print("\nAction selections at High Queue:")
print(q_high["Action"].value_counts(normalize=True))

# Breakdown by mode and config at high queue
m["Action_high"] = m["Action_high"]
print("\nAction selection at Q=100M by Mode and Config:")
print(m.groupby(["Mode", "Config", "Action_high"]).size() / m.groupby(["Mode", "Config"]).size())
