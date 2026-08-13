# CANONICAL_BASELINE_REPORT.md

Campaign ID: `CAMPAIGN_CANONICAL_20260802`  
Created: 2026-08-02T17:47:20Z  
Code hash (sha256 over frozen protocol files): `3050d0c285f9ee28...`  

## Status

- Expected combinations: 45 (methods ['ma-rope', 'alloffload', 'nooffload'] x densities [8, 16, 32] x seeds [0, 1, 2, 3, 4])
- Complete: 45
- In progress (checkpointed, resumable): 0
- Not yet started: 0

## Protocol

- Environment: `env/environment.py:V2XEnv`, `env_mode="baseline_recreation"`
- Training/eval logic: `scripts/reproduce_paper_sweeps.py` (`train_ma_rope`/`evaluate_policy`), reproduced/imported unmodified
- Explicitly excluded: env/environment_plus.py:V2XEnvPlus, scripts/train_b3_baselines.py
- Wu2021: NOT INCLUDED: no Wu2021 baseline implementation exists anywhere in the recovered codebase (grep across all .py files for 'wu2021'/'wu_2021' found zero matches). Not canonical/functional; excluded per instruction.

### Known protocol gap, fixed in the orchestrator only

Original train_ma_rope()/D3QNAgent never call torch.manual_seed(); network weight init draws from torch's unseeded global RNG. Verified empirically: 3 fresh-process constructions of the same DuelingQNetwork(12,11) produced 3 different first-weight values. This orchestrator calls torch.manual_seed(seed) before constructing each agent/coordinator so runs are reproducible across the chunked, multi-process execution this sandbox requires. No environment, algorithm, or metric formula was changed.

## MA-ROPE execution summary (complete)

All 15 MA-ROPE combinations finished. Actual measured training time per combo, read directly from the manifest (not estimated):

| N (vehicles) | Seeds complete | Mean training time/seed | Total |
|---|---|---|---|
| 8 | 5/5 | 76.3s | 381.6s |
| 16 | 5/5 | 140.0s | 700.1s |
| 32 | 5/5 | 283.6s | 1418.1s |

Sum of all recorded per-combo training durations: 2499.7s (cross-check this against the executor's reported wall-clock time -- they should be close; a large mismatch would indicate something ran outside what the manifest recorded).

Every combo recorded `step_count=10000, fedavg_rounds=200` (100 episodes x 100 steps, FedAvg every 50 steps) -- the expected control-flow signature of a genuine, complete run, checked here rather than assumed.

## What's real right now

- All 30 AllOffload/NoOffload combinations: genuinely executed, real metrics, in `CANONICAL_BASELINE_RESULTS.csv`.
- MA-ROPE combinations complete: 15 (ma-rope_n8_seed0, ma-rope_n8_seed1, ma-rope_n8_seed2, ma-rope_n8_seed3, ma-rope_n8_seed4, ma-rope_n16_seed0, ma-rope_n16_seed1, ma-rope_n16_seed2, ma-rope_n16_seed3, ma-rope_n16_seed4, ma-rope_n32_seed0, ma-rope_n32_seed1, ma-rope_n32_seed2, ma-rope_n32_seed3, ma-rope_n32_seed4)
- MA-ROPE combinations with real partial training progress (checkpointed, resumable, not fabricated): 0

## Full results table

See `CANONICAL_BASELINE_RESULTS.csv` -- contains exactly the complete combinations, no placeholders, no interpolated or copied-from-manuscript values.

## Next steps

Campaign complete. Proceed to independent validation against EXECUTION_CONTRACT.md section 9 (manifest completeness, checkpoint hash recomputation, structural invariants, code-hash consistency) before these numbers are used for any Phase 4 root-cause analysis or manuscript revision.
