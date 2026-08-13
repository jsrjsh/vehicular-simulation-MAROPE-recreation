"""
scripts/run_training_duration_diagnostic.py

Answers one specific, pre-registered question (per QUEUE_LOSS_ROOT_CAUSE_REPORT.md's open item and
the PI-level publication decision): is MA-ROPE's occasional use of the less-reliable WiFi6 RAT a
converged policy tradeoff, or an artifact of a not-fully-converged 100-episode training run?

Method: train MA-ROPE (same environment, same algorithm, same hyperparameters as the corrected
canonical campaign -- reuses run_corrected_campaign.py's train_ma_rope_resumable() and
evaluate_policy_v2() unmodified) to three increasing durations -- 100 (the existing protocol's
length), 250, and 500 episodes -- evaluating at each checkpoint with the standard 5-episode eval
protocol plus action/RAT-distribution tracking (evaluate_policy_v2(..., track_actions=True)).

This is a DIAGNOSTIC, not a new campaign: results land in their own directory
(results/CAMPAIGN_TRAINING_DURATION_<id>/), never mixed with results/corrected_v2_staging/ or any
CAMPAIGN_CORRECTED_* directory, and the checkpoint/resume state used here is entirely separate from
the main corrected campaign's -- training this diagnostic's N=32/seed=0 run does NOT reuse or
perturb the main campaign's own N=32/seed=0 checkpoint.

Starts with ONE seed at N=32 (seed 0, matching the density/seed most relevant to the queue-loss
investigation this diagnostic follows up on). Per the standing instruction, expansion to five seeds
is a judgment call to be made by reviewing this seed's results first (does the action distribution
or the failure-rate/OTR/energy trend materially change between 100->250->500 episodes?) -- this
script does not auto-expand; it reports one seed's trajectory and stops, exactly as specified.

Usage:
  PYTHONPATH=<workspace> python3 scripts/run_training_duration_diagnostic.py \
      --n-agents 32 --seed 0 --checkpoints 100,250,500 --budget-seconds 999999
"""
import os
import sys
import csv
import json
import time
import argparse
import datetime
import shutil

from scripts.run_corrected_campaign import (
    ENV_MODE, compute_code_hash, train_ma_rope_resumable, evaluate_policy_v2, get_checkpoint_hash,
)

DEFAULT_CHECKPOINTS = [100, 250, 500]


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _merge_and_save_manifest(manifest_path, manifest):
    """
    Reload-and-merge before writing, not a blind overwrite. Discovered a real bug (2026-08-03): when
    two seeds of this diagnostic are launched concurrently against the SAME diagnostic-id (as
    happened when AG ran seed=1 and seed=2 in parallel background processes), each process holds its
    own long-lived in-memory copy of `manifest` loaded at start-up. A naive `json.dump(manifest, ...)`
    at the end of each checkpoint blindly overwrites the file with that process's own view -- whichever
    process writes last wins, silently discarding any keys the OTHER process had already written
    (seed=1's three entries were dropped this way; recovered by reconstructing them from
    TRAINING_DURATION_RESULTS.csv + the checkpoint files, since the CSV is append-only and unaffected).
    Fix: immediately before every write, re-read whatever is currently on disk and merge its "runs"
    dict UNDER this process's own (so this process's own latest data always wins for its own keys,
    but any other process's already-written keys are preserved rather than clobbered). Not perfectly
    atomic (a race window remains between the reload and the write), but eliminates the actual failure
    mode observed, which unfolded over many minutes, not milliseconds.
    """
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            on_disk = json.load(f)
        merged_runs = dict(on_disk.get("runs", {}))
        merged_runs.update(manifest["runs"])  # this process's own latest entries take precedence for its own keys
        manifest = dict(on_disk)
        manifest["runs"] = merged_runs
    tmp = manifest_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    os.replace(tmp, manifest_path)
    return manifest


def run_diagnostic(diagnostic_id, n_agents=32, seed=0, checkpoints=None, budget_seconds=999999):
    checkpoints = checkpoints or DEFAULT_CHECKPOINTS
    diag_dir = f"results/{diagnostic_id}"
    raw_dir = f"{diag_dir}/raw"
    resume_dir = f"{diag_dir}/_resume_state"  # dedicated -- never shared with the main campaign
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(resume_dir, exist_ok=True)

    manifest_path = f"{diag_dir}/manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
    else:
        code_hash, per_file_hashes = compute_code_hash()
        manifest = {
            "diagnostic_id": diagnostic_id,
            "purpose": (
                "Determine whether MA-ROPE's WiFi6 over-reliance (identified in "
                "QUEUE_LOSS_ROOT_CAUSE_REPORT.md) is a converged policy tradeoff or an artifact of "
                "the standard 100-episode training protocol not having converged."
            ),
            "created_utc": _now_iso(),
            "n_agents": n_agents,
            "seed": seed,
            "checkpoints_requested": checkpoints,
            "env_mode": ENV_MODE,
            "code_hash_sha256": code_hash,
            "per_file_hashes": per_file_hashes,
            "command": " ".join(sys.argv),
            "note": (
                "Single seed by design -- see module docstring. Do not expand to additional seeds "
                "without first reviewing whether this seed's results materially change across "
                "checkpoints; that is a judgment call for the reviewing scientist, not this script."
            ),
            "runs": {},
        }

    csv_path = f"{diag_dir}/TRAINING_DURATION_RESULTS.csv"
    write_header = not os.path.exists(csv_path)
    csv_file = open(csv_path, "a", newline="")
    csv_writer = csv.writer(csv_file)
    if write_header:
        csv_writer.writerow([
            "n_agents", "seed", "episodes_trained", "checkpoint_hash", "step_count", "fedavg_rounds",
            "cumulative_training_duration_s", "eval_duration_s",
            "u_prr_active", "u_otr_active", "fleet_otr", "prr",
            "conditional_tx_failure_rate", "fleet_tx_failure_rate",
            "fleet_tx_failure_count_total", "fleet_tx_attempt_count_total", "total_vehicle_steps_total",
            "energy_active", "latency_active",
            "mean_realised_rho", "action_distribution_json", "rat_usage_json",
            "completed_utc",
        ])

    for target_episodes in checkpoints:
        key = f"n{n_agents}_seed{seed}_ep{target_episodes}"
        if manifest["runs"].get(key, {}).get("status") == "complete":
            print(f"[skip] {key} already complete")
            continue

        finished, coord, ckpt_hash, step_count, fedavg_rounds, cum_runtime = train_ma_rope_resumable(
            ENV_MODE, n_agents, seed, resume_dir, episodes=target_episodes, budget_seconds=budget_seconds
        )
        if not finished:
            manifest["runs"][key] = {
                "status": "in_progress", "episodes_target": target_episodes,
                "cumulative_runtime_s": cum_runtime, "last_updated_utc": _now_iso(),
            }
            manifest = _merge_and_save_manifest(manifest_path, manifest)
            print(f"[in_progress] {key}: {cum_runtime:.1f}s cumulative, budget exhausted this call")
            csv_file.close()
            return manifest

        t0 = time.time()
        metrics = evaluate_policy_v2(ENV_MODE, "ma-rope", n_agents, seed, coord=coord, episodes=5, track_actions=True)
        eval_dur = time.time() - t0

        # Copy the final checkpoint into this diagnostic's own raw/ with a duration-tagged name so
        # it can never be confused with the main corrected campaign's ma-rope_seed{S}.pt.
        src_pt = f"results/corrected_v2_staging/n{n_agents}/ma-rope_seed_{seed}_ep_{target_episodes}_hash_{ckpt_hash}.pt"
        dest_pt = f"{raw_dir}/ma-rope_seed{seed}_ep{target_episodes}_hash{ckpt_hash}.pt"
        if os.path.exists(src_pt) and not os.path.exists(dest_pt):
            shutil.copy2(src_pt, dest_pt)

        csv_writer.writerow([
            n_agents, seed, target_episodes, ckpt_hash, step_count, fedavg_rounds,
            f"{cum_runtime:.3f}", f"{eval_dur:.3f}",
            metrics["u_prr_active"], metrics["u_otr_active"], metrics["fleet_otr"], metrics["prr"],
            metrics["conditional_tx_failure_rate"], metrics["fleet_tx_failure_rate"],
            metrics["fleet_tx_failure_count_total"], metrics["fleet_tx_attempt_count_total"],
            metrics["total_vehicle_steps_total"],
            metrics["energy_active"], metrics["latency_active"],
            metrics["mean_realised_rho"],
            json.dumps(metrics["action_distribution"]), json.dumps(metrics["rat_usage"]),
            _now_iso(),
        ])
        csv_file.flush()

        manifest["runs"][key] = {
            "status": "complete", "episodes_target": target_episodes,
            "checkpoint_hash": ckpt_hash, "step_count": step_count, "fedavg_rounds": fedavg_rounds,
            "training_duration_s": cum_runtime, "eval_duration_s": eval_dur,
            "dest_checkpoint": dest_pt, "metrics": metrics, "completed_utc": _now_iso(),
        }
        manifest = _merge_and_save_manifest(manifest_path, manifest)
        print(f"[complete] {key}: train {cum_runtime:.1f}s + eval {eval_dur:.2f}s, "
              f"conditional_tx_failure_rate={metrics['conditional_tx_failure_rate']:.4f}, "
              f"fleet_tx_failure_rate={metrics['fleet_tx_failure_rate']:.4f}, "
              f"rat_usage={metrics['rat_usage']}")

    csv_file.close()
    return manifest


def generate_execution_report(diagnostic_id):
    """Writes EXECUTION_REPORT.md summarizing the raw trajectory across checkpoints -- data only,
    no interpretation, per the standing instruction ('Do not interpret the science')."""
    diag_dir = f"results/{diagnostic_id}"
    manifest_path = f"{diag_dir}/manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    lines = ["# EXECUTION_REPORT.md", "", f"Diagnostic ID: `{diagnostic_id}`",
             f"Purpose: {manifest['purpose']}", "", "## Raw trajectory (data only, no interpretation)", ""]
    lines.append("| Episodes trained | Checkpoint hash | conditional_tx_failure_rate | fleet_tx_failure_rate | Fleet OTR | Energy (active) | Latency (active) | RAT usage (0=Local,1=LTE,2=ITS-G5,3=WiFi6,4=5G-NR) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for key, run in sorted(manifest["runs"].items(), key=lambda kv: kv[1].get("episodes_target", 0)):
        if run.get("status") != "complete":
            lines.append(f"| {run.get('episodes_target', '?')} | (incomplete: {run.get('status')}) | | | | | | |")
            continue
        m = run["metrics"]
        lines.append(
            f"| {run['episodes_target']} | `{run['checkpoint_hash']}` | "
            f"{m['conditional_tx_failure_rate']:.4f} | {m['fleet_tx_failure_rate']:.4f} | "
            f"{m['fleet_otr']:.4f} | {m['energy_active']:.4f} | {m['latency_active']:.2f} | "
            f"{m['rat_usage']} |"
        )
    lines.append("")
    out_path = f"{diag_dir}/EXECUTION_REPORT.md"
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostic-id", type=str, default="CAMPAIGN_TRAINING_DURATION_20260803")
    parser.add_argument("--n-agents", type=int, default=32)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--checkpoints", type=str, default="100,250,500")
    parser.add_argument("--budget-seconds", type=float, default=999999)
    parser.add_argument("--report-only", action="store_true", help="regenerate EXECUTION_REPORT.md from existing manifest.json only")
    args = parser.parse_args()

    if args.report_only:
        generate_execution_report(args.diagnostic_id)
        sys.exit(0)

    checkpoints = [int(x) for x in args.checkpoints.split(",")]
    run_diagnostic(args.diagnostic_id, n_agents=args.n_agents, seed=args.seed,
                    checkpoints=checkpoints, budget_seconds=args.budget_seconds)
    generate_execution_report(args.diagnostic_id)
