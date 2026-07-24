import pandas as pd

df = pd.read_csv('analysis/QUEUE_SENSITIVITY_RAW.csv')

# Parse Mode and Config from ModelPath
df["Mode"] = df["ModelPath"].apply(lambda x: x.split("/")[1].split("_")[0])
df["Config"] = df["ModelPath"].apply(lambda x: "Candidate_" + x.split("/")[1].split("_")[2] if "Candidate" in x else "Baseline")
df["Seed"] = df["ModelPath"].apply(lambda x: x.split("seed_")[1].split("/")[0])

# Filter Candidate_B only
df_b = df[df["Config"] == "Candidate_B"]

# S_Q calculation
q_low = df_b[df_b["Queue"] == 0.0].copy()
q_high = df_b[df_b["Queue"] == 100e6].copy()

m = pd.merge(q_low, q_high, on=["ModelPath", "ClientIdx", "Scenario", "SupportType", "Mode", "Config", "Seed"], suffixes=("_low", "_high"))
m["S_Q"] = m["DeltaQ_5G_Loc_low"] - m["DeltaQ_5G_Loc_high"]

print("--- S_Q Distribution by Mode for Candidate B ---")
print(m.groupby(["Mode"])["S_Q"].describe())

print("\n--- S_Q by Seed ---")
print(m.groupby(["Mode", "Seed"])["S_Q"].mean())
