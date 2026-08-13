# CORRECTED_BASELINE_REPORT.md

Path B: corrected MA-ROPE campaign. See QUEUE_LOSS_ROOT_CAUSE_REPORT.md for the scientific verdict this campaign corrects for, and run_corrected_campaign.py's module docstring for the exact list of changes vs. the frozen Path A baseline (CAMPAIGN_CANONICAL_20260802).

Campaign ID: `CAMPAIGN_CORRECTED_20260803`  
Created: 2026-08-03T06:56:51Z  
Code hash (sha256 over frozen protocol files): `3050d0c285f9ee28...`  

## Status

- Expected combinations: 75 (methods ['ma-rope', 'alloffload', 'nooffload', 'ucb_bandit', 'coopec_greedy'] x densities [8, 16, 32] x seeds [0, 1, 2, 3, 4])
- Complete: 75
- In progress (checkpointed, resumable): 0
- Not yet started: 0

## Protocol

- Path: Path B: corrected MA-ROPE (see QUEUE_LOSS_ROOT_CAUSE_REPORT.md)
- Environment: `env/environment.py:V2XEnv`, `env_mode="baseline_recreation"`
- Script: scripts/run_corrected_campaign.py (train loop mirrors reproduce_paper_sweeps.py's train_ma_rope() exactly; evaluate_policy_v2() mirrors evaluate_policy() exactly except metric naming/additions)
- Explicitly excluded: env/environment_plus.py:V2XEnvPlus, scripts/train_b3_baselines.py
- Wu2021: NO FAITHFUL REPRODUCTION EXISTS: no Wu2021 implementation with verifiable fidelity to the cited paper exists anywhere in the recovered codebase, and the manuscript's own citation/description of Wu2021 provides no equations, pseudocode, or hyperparameters (only a one-line gloss and an internally-tensioned feature-table entry). In its place, this campaign includes 'ucb_bandit' -- a disclosed, non-faithful RECONSTRUCTION (stateless UCB1 over 4 arms: Local + 5G-NR at 25/50/100%, one independent bandit per vehicle) consistent with Wu2021's stated feature-table properties (single-RAT, no partial-rho, no FL privacy). Report this column as 'UCB-RAT (Wu2021-inspired reconstruction)' -- never as 'Wu2021' unqualified. See scripts/run_corrected_campaign.py's UCB_ARMS comment block and EXECUTION_CONTRACT_V3.md section 0 for full rationale.

### Changes vs. Path A baseline

- metric rename: queue_loss -> conditional_tx_failure_rate (identical computation, only the name changed)
- new metrics added: fleet_tx_failure_rate, fleet_tx_failure_count, fleet_tx_attempt_count, total_vehicle_steps
- checkpoint persistence fixed: all N agents' state_dicts are now saved (previously only agent 0)

### Unchanged from Path A: environment physics, D3QN/PER/FedAvg algorithm, all hyperparameters, all other metrics (U_PRR, U_OTR, fleet_otr, energy, latency)

### Known protocol gap, fixed in the orchestrator only (inherited from Path A, unrelated to the Path B correction)

Original train_ma_rope()/D3QNAgent never call torch.manual_seed(); network weight init draws from torch's unseeded global RNG. Verified empirically: 3 fresh-process constructions of the same DuelingQNetwork(12,11) produced 3 different first-weight values. This orchestrator calls torch.manual_seed(seed) before constructing each agent/coordinator so runs are reproducible across the chunked, multi-process execution this sandbox requires. No environment, algorithm, or metric formula was changed.

## Metric definitions (read this before comparing to any older report)

- `conditional_tx_failure_rate`: failures / attempted transmissions only (chosen_rat>0 and chosen_rho>0.0). Numerically identical to the old `queue_loss` column -- renamed, not recomputed, per QUEUE_LOSS_ROOT_CAUSE_REPORT.md's finding that no queue-capacity-drop mechanism exists anywhere in the code.
- `fleet_tx_failure_rate`: failures / ALL vehicle-steps (every generated task, whether or not an offload was attempted). This is the denominator that does NOT reverse the MA-ROPE-vs-AllOffload ordering seen under the old denominator.
- `fleet_tx_failure_count_total` / `fleet_tx_attempt_count_total` / `total_vehicle_steps_total`: absolute counts backing the two rates above, summed across all 5 eval episodes for the combo.

## MA-ROPE execution summary (complete)

All 15 MA-ROPE combinations finished. Actual measured training time per combo, read directly from the manifest (not estimated):

| N (vehicles) | Seeds complete | Mean training time/seed | Total |
|---|---|---|---|
| 8 | 5/5 | 70.8s | 354.1s |
| 16 | 5/5 | 143.5s | 717.3s |
| 32 | 5/5 | 288.9s | 1444.7s |

Sum of all recorded per-combo training durations: 2516.0s (cross-check this against the executor's reported wall-clock time -- they should be close; a large mismatch would indicate something ran outside what the manifest recorded).

Every combo recorded `step_count=10000, fedavg_rounds=200` (100 episodes x 100 steps, FedAvg every 50 steps) -- the expected control-flow signature of a genuine, complete run, checked here rather than assumed.

### Checkpoint content check

Unlike Path A, each `ma-rope_seed{S}.pt` here should contain `all_agent_online_net_state_dicts` with exactly `n_agents` entries (not just agent 0's weights) -- verified generically by `run_corrected_campaign.py --verify-fidelity` before this campaign was started; spot-check a real file from this campaign directly:
`torch.load(path)["all_agent_online_net_state_dicts"]` should have length == N for that combo's density.

## What's real right now

- All 60 AllOffload/NoOffload/UCB-bandit/CoopEC-greedy combinations (no separate training phase): genuinely executed, real metrics, in `CORRECTED_BASELINE_RESULTS.csv`.
- MA-ROPE combinations complete: 15 (ma-rope_n8_seed0, ma-rope_n8_seed1, ma-rope_n8_seed2, ma-rope_n8_seed3, ma-rope_n8_seed4, ma-rope_n16_seed0, ma-rope_n16_seed1, ma-rope_n16_seed2, ma-rope_n16_seed3, ma-rope_n16_seed4, ma-rope_n32_seed0, ma-rope_n32_seed1, ma-rope_n32_seed2, ma-rope_n32_seed3, ma-rope_n32_seed4)
- MA-ROPE combinations with real partial training progress (checkpointed, resumable, not fabricated): 0

## Full results table

See `CORRECTED_BASELINE_RESULTS.csv` -- contains exactly the complete combinations, no placeholders, no interpolated or copied-from-manuscript/Path-A values.

## Next steps

Campaign complete. Proceed to independent validation against EXECUTION_CONTRACT_V2.md's pass/fail checklist, then to the manuscript-impact memo.
