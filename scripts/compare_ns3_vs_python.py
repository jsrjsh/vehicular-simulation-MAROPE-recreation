"""
scripts/compare_ns3_vs_python.py

Table-by-table comparison of the ns-3 + SUMO baseline sweep
(results/ns3_eval_baselines/*.csv, from scripts/ns3_eval_baselines.py)
against CAMPAIGN_PHYSICS_FIX_20260818 (the reference Python campaign,
combining both the log10-latency fix and the Jakes-fading GHz->Hz fix --
see NS3_SUMO_STATUS.md for why this is the right comparison target, not
v25 or CAMPAIGN_LATENCY_FIX_20260815).

Only meaningful once both sweeps were run under the episode-level seed fix
(2026-08-18, see NS3_SUMO_STATUS.md "Seed-threading bug, round 2") -- earlier
ns-3 CSVs are known-bad (identical trajectories replayed across episodes)
and will silently produce misleadingly tight numbers if fed into this
script without re-running the sweep first.

Usage: python3 scripts/compare_ns3_vs_python.py
"""
import glob
import os
import re

import pandas as pd

NS3_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "ns3_eval_baselines")
PYTHON_CAMPAIGN_DIR = os.path.join(
    os.path.dirname(__file__), "..", "_claude_workspace", "results",
    "CAMPAIGN_PHYSICS_FIX_20260818", "raw"
)

METRICS = ["fleet_otr", "prr", "u_otr_active", "u_prr_active",
           "latency_active_ms", "conditional_tx_failure_rate", "fleet_tx_failure_rate"]

FNAME_RE = re.compile(r"^(?P<policy>[a-z_-]+)_n(?P<n>\d+)_seed(?P<seed>\d+)\.csv$")


def load_ns3():
    rows = []
    for f in glob.glob(os.path.join(NS3_DIR, "*.csv")):
        m = FNAME_RE.match(os.path.basename(f))
        if not m:
            raise ValueError(f"filename doesn't match expected <policy>_n<N>_seed<S>.csv pattern: {f}")
        df = pd.read_csv(f)
        df["policy_type"] = m.group("policy")
        df["n_vehicles"] = int(m.group("n"))
        df["seed"] = int(m.group("seed"))
        rows.append(df)
    if not rows:
        return None
    return pd.concat(rows, ignore_index=True)


def load_python_campaign():
    rows = []
    for f in glob.glob(os.path.join(PYTHON_CAMPAIGN_DIR, "n*", "*.csv")):
        n = int(os.path.basename(os.path.dirname(f)).replace("n", ""))
        df = pd.read_csv(f)
        df["n_vehicles"] = n
        rows.append(df)
    if not rows:
        return None
    return pd.concat(rows, ignore_index=True)


def summarize(df, label):
    present = [m for m in METRICS if m in df.columns]
    g = df.groupby(["n_vehicles", "policy_type"])[present].mean()
    g.columns = pd.MultiIndex.from_product([[label], g.columns])
    return g


def main():
    ns3_df = load_ns3()
    py_df = load_python_campaign()

    if ns3_df is None:
        print(f"No ns-3 CSVs found in {NS3_DIR} -- nothing to compare yet.")
        return
    if py_df is None:
        print(f"No Python campaign CSVs found in {PYTHON_CAMPAIGN_DIR}.")
        return

    ns3_summary = summarize(ns3_df, "ns3")
    py_summary = summarize(py_df, "python")

    merged = ns3_summary.join(py_summary, how="outer")

    for metric in METRICS:
        ns3_col = ("ns3", metric)
        py_col = ("python", metric)
        if ns3_col in merged.columns and py_col in merged.columns:
            merged[("diff", metric)] = merged[ns3_col] - merged[py_col]

    merged = merged.sort_index(axis=1, level=0)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)

    for metric in METRICS:
        cols = [c for c in [("ns3", metric), ("python", metric), ("diff", metric)] if c in merged.columns]
        if not cols:
            continue
        print(f"\n=== {metric} ===")
        print(merged[cols].round(4))

    out_path = os.path.join(os.path.dirname(__file__), "..", "results", "ns3_vs_python_comparison.csv")
    merged.to_csv(out_path)
    print(f"\nWrote full comparison table to {out_path}")


if __name__ == "__main__":
    main()
