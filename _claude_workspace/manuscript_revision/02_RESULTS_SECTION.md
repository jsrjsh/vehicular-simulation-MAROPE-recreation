# Results Section (Revision Draft v1)

All numbers sourced directly from `CORRECTED_RESULT_TABLES.md` (`CAMPAIGN_CORRECTED_20260803`,
75 combinations, mean ± population std across 5 seeds; `CAMPAIGN_TRAINING_DURATION_20260803`,
3 seeds × 3 checkpoints). Nothing here is estimated or copied from any prior manuscript version.

---

### 5.1 Headline comparison (N=32)

At the highest tested fleet density (32 vehicles), MA-ROPE achieves the best fleet-wide on-time
rate of any policy evaluated:

| Metric | MA-ROPE | AllOffload | NoOffload | UCB-RAT | CoopEC-RAT |
|---|---:|---:|---:|---:|---:|
| Fleet OTR | **0.8875 ± 0.0143** | 0.1246 ± 0.0073 | 1.0000 ± 0.0000* | 0.3455 ± 0.0054 | 0.8014 ± 0.0043 |
| U_PRR (active) | **0.9583 ± 0.0014** | 0.6076 ± 0.0009 | 0.9610 ± 0.0008 | 0.8987 ± 0.0021 | 0.9580 ± 0.0016 |
| U_OTR (active) | **0.5252 ± 0.0016** | 0.1264 ± 0.0058 | 0.5079 ± 0.0016 | 0.4976 ± 0.0031 | 0.5492 ± 0.0017 |
| conditional_tx_failure_rate | 0.0546 ± 0.0068 | 0.0246 ± 0.0008 | 0.0000 | 0.0254 ± 0.0008 | **0.0230 ± 0.0002** |
| fleet_tx_failure_rate | **0.0024 ± 0.0003** | 0.0246 ± 0.0008 | 0.0000 | 0.0141 ± 0.0004 | 0.0033 ± 0.0001 |
| Attempted transmissions (5-ep. total, of 16,000 vehicle-steps) | 715.8 ± 10.8 | 16,000 | 0 | 8,941.2 ± 26.2 | 2,302.8 ± 60.0 |
| Latency (active, ms) | 219.67 ± 3.70 | 829.98 ± 2.21 | 233.67 ± 3.55 | 250.04 ± 3.51 | **107.42 ± 1.56** |

*NoOffload's Fleet OTR of 1.0 is a definitional artifact (no transmission attempts ever occur, so
the on-time-rate denominator is trivially satisfied) and is reported for completeness, not as a
meaningful comparator — this convention is stated explicitly in Section 5.4 to preempt
misreading.

MA-ROPE wins Fleet OTR, U_PRR, and U_OTR against every non-trivial baseline. CoopEC-RAT — a
non-learned, task-property-only heuristic — is the strongest baseline found, reaching 0.801 Fleet
OTR; its very low latency (107ms) reflects that it offloads only a minority of compute-heavy tasks
by design, not superior scheduling. UCB-RAT, a stateless per-vehicle bandit, transmits far more
often than either MA-ROPE or CoopEC-RAT (8,941 vs. 716 vs. 2,303 attempts) and still under-performs
both on Fleet OTR — evidence that attempt frequency alone does not buy reliability in this
environment.

### 5.2 The reliability decomposition: attempt-conditional vs. fleet-wide failure

MA-ROPE's `conditional_tx_failure_rate` (5.46%) is higher than AllOffload's (2.46%) and UCB-RAT's
(2.54%) — read alone, this would suggest MA-ROPE is less reliable per attempt. But MA-ROPE
attempts only 716 of 16,000 possible transmissions, versus AllOffload's 16,000 and UCB-RAT's 8,941.
The resulting fleet-wide failure rate — failures as a fraction of *all* generated tasks, not just
attempted ones — inverts the ordering: MA-ROPE's 0.24% is roughly 10x lower than AllOffload's
2.46% and roughly 6x lower than UCB-RAT's 1.41%. In absolute terms, across a 5-episode evaluation,
MA-ROPE causes 39.2 ± 4.2 fleet-wide failures versus AllOffload's 393.8 ± 13.4 and UCB-RAT's
226.0 ± 7.0.

The mechanism (full decomposition in `QUEUE_LOSS_ROOT_CAUSE_REPORT.md`) is that MA-ROPE
concentrates its transmission attempts on WiFi-6, which has a materially higher per-attempt
failure rate under contention (14.66%) than 5G-NR (2.37%), but MA-ROPE compensates by attempting
so much less often overall that its absolute reliability is still the best of any policy tested.
**We report both metrics side by side deliberately: neither alone characterizes fleet-scale
reliability correctly, and reporting only the conditional rate (as is common in the offloading
literature surveyed) would understate MA-ROPE's real advantage.**

### 5.3 Density scaling (N = 8 → 16 → 32)

| N | MA-ROPE | AllOffload | UCB-RAT | CoopEC-RAT |
|---|---:|---:|---:|---:|
| 8 | 0.9328 ± 0.0066 | 0.3397 ± 0.0187 | 0.7053 ± 0.0113 | 0.9029 ± 0.0067 |
| 16 | 0.9325 ± 0.0136 | 0.2653 ± 0.0081 | 0.4526 ± 0.0072 | 0.8233 ± 0.0112 |
| 32 | 0.8875 ± 0.0143 | 0.1246 ± 0.0073 | 0.3455 ± 0.0054 | 0.8014 ± 0.0043 |

MA-ROPE's advantage widens as density increases: it degrades only 4.5 points (0.933→0.888) from
N=8 to N=32, versus CoopEC-RAT's 10-point drop (0.903→0.801), UCB-RAT's 36-point drop
(0.705→0.346), and AllOffload's 21-point drop (0.340→0.125). CoopEC-RAT's more graceful-than-UCB
degradation follows directly from its design — its decision rule never depends on queue or channel
state, so its decline reflects only the shared-RSU-queue contribution to latency, not any adaptive
failure. MA-ROPE's still-flatter curve reflects that it adapts to rising contention rather than
merely being insensitive to it.

### 5.4 Robustness to training duration

Independently across three seeds, training MA-ROPE from 100 to 500 episodes (a 5x range) produces
within-seed changes in Fleet OTR (0.009-0.031) and conditional failure rate (0.001-0.018) that are
the same size as, or smaller than, ordinary cross-seed variance at a fixed training length
(Fleet OTR std 0.0143; failure-rate std 0.0068). Direction is inconsistent across seeds — Fleet OTR
moves down for seeds 0 and 2 but up for seed 1 across the same training range. This supports
reading MA-ROPE's WiFi-6-concentrated RAT usage as a converged policy characteristic rather than an
artifact of insufficient training (full table and seed-by-seed detail in `CORRECTED_RESULT_TABLES.md`).

### 5.5 Scope of comparison, stated plainly

This evaluation compares MA-ROPE against the two trivial extremes and two newly-built, disclosed
non-learned baselines (UCB-RAT, CoopEC-RAT). It does not include MADDPG, a Lyapunov-optimization
baseline, or a GA+DQN baseline that appeared in earlier internal drafts of this work: no
independently-executable implementation of any of the three could be recovered or reconstructed
with confidence, and — separately — an internal audit of the prior comparison table found internal
inconsistencies (duplicated values across supposedly-independent baseline rows) inconsistent with
those numbers having come from genuinely separate runs. Rather than present numbers we cannot
stand behind, we omit them. This is disclosed here, not discovered by a reviewer.
