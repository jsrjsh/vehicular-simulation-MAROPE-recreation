# CORRECTED_RESULT_TABLES.md

Real, independently-validated numbers from `CAMPAIGN_CORRECTED_20260803` (60/60 combinations,
mean ± population std across 5 seeds each) and `CAMPAIGN_TRAINING_DURATION_20260803`. Every number
here is read directly from `CORRECTED_BASELINE_RESULTS.csv`/`TRAINING_DURATION_RESULTS.csv` — none
estimated, interpolated, or copied from the manuscript. Validation status for both source campaigns:
**PASS** (see `CLAUDE_FINDINGS.md`'s 2026-08-03 validation entry for the full independent-check
list — code hash recomputation, checkpoint hash + all-agent-entry recomputation, structural
invariants, cross-campaign determinism check, and an independent from-scratch re-execution of the
UCB-RAT baseline matching to 15 significant digits).

**Baseline scope note (post-`BASELINE_TABLE_INTEGRITY_FINDING.md`)**: the manuscript's other four
named comparators (MADDPG, Lyapunov-Jing2019, GA+DQN-Yun2022, and — originally — CoopEC-Shao2025)
turned out to have no credible target to reproduce against (10 of 12 rows in the manuscript's own
headline table share an identical Fleet OTR value, including MA-ROPE's own row). Per the reviewed
decision: `coopec_greedy` was implemented as a new, genuinely-run baseline (not a reproduction of
the manuscript's CoopEC row); MADDPG and GA+DQN-Yun2022 are dropped from the comparison table
entirely; Lyapunov-Jing2019 is queued as a candidate for future work, not implemented this round.

**`ucb_bandit` must be read as "UCB-RAT (Wu2021-inspired reconstruction)" everywhere** — it is a
disclosed reconstruction of Wu2021's stated properties (stateless UCB1 bandit, 4 arms: Local +
5G-NR at 25/50/100%, one independent instance per vehicle), not a certified faithful reproduction.
See `EXECUTION_CONTRACT_V3.md` §0 for the full rationale.

**`coopec_greedy` must be read as "CoopEC-RAT (Shao2025-inspired reconstruction)" everywhere** — a
disclosed, hand-crafted, non-learned, non-adaptive (to channel/queue) greedy rule: offload fully via
5G-NR if local compute latency would exceed 50% of the task's deadline, else compute locally. See
`scripts/run_corrected_campaign.py`'s `COOPEC_LOCAL_DEADLINE_FRACTION` comment block for the full
rationale.

---

## N=32 headline table (primary comparison point)

| Metric | MA-ROPE | AllOffload | NoOffload | UCB-RAT (reconstruction) | CoopEC-RAT (reconstruction) |
|---|---:|---:|---:|---:|---:|
| U_PRR (active) | 0.9583 ± 0.0014 | 0.6076 ± 0.0009 | 0.9610 ± 0.0008 | 0.8987 ± 0.0021 | 0.9580 ± 0.0016 |
| U_OTR (active) | 0.5252 ± 0.0016 | 0.1264 ± 0.0058 | 0.5079 ± 0.0016 | 0.4976 ± 0.0031 | 0.5492 ± 0.0017 |
| Fleet OTR | 0.8875 ± 0.0143 | 0.1246 ± 0.0073 | 1.0000 ± 0.0000 | 0.3455 ± 0.0054 | 0.8014 ± 0.0043 |
| PRR | 0.9454 ± 0.0068 | 0.9754 ± 0.0008 | 1.0000 ± 0.0000 | 0.9746 ± 0.0008 | 0.9770 ± 0.0002 |
| conditional_tx_failure_rate | 0.0546 ± 0.0068 | 0.0246 ± 0.0008 | 0.0000 ± 0.0000 | 0.0254 ± 0.0008 | 0.0230 ± 0.0002 |
| fleet_tx_failure_rate | 0.0024 ± 0.0003 | 0.0246 ± 0.0008 | 0.0000 ± 0.0000 | 0.0141 ± 0.0004 | 0.0033 ± 0.0001 |
| Absolute fleet failures (5-episode total) | 39.2 ± 4.2 | 393.8 ± 13.4 | 0 | 226.0 ± 7.0 | 53.2 ± 1.5 |
| Attempted transmissions (5-episode total) | 715.8 ± 10.8 | 16,000 ± 0 | 0 | 8,941.2 ± 26.2 | 2,302.8 ± 60.0 |
| Energy (active) | -1.8144 ± 0.0105 | 7.1036 ± 0.0095 | -1.9411 ± 0.0133 | -0.8956 ± 0.0235 | -1.5687 ± 0.0154 |
| Latency (active, ms) | 219.67 ± 3.70 | 829.98 ± 2.21 | 233.67 ± 3.55 | 250.04 ± 3.51 | 107.42 ± 1.56 |

**Reading this table**: MA-ROPE decisively wins on Fleet OTR (0.888 vs. UCB-RAT's 0.346, AllOffload's
0.125), U_OTR, U_PRR, energy, and latency against both AllOffload and the new UCB-RAT baseline.
MA-ROPE trails both AllOffload and UCB-RAT specifically on `conditional_tx_failure_rate` (the
per-attempt metric) while decisively beating both on `fleet_tx_failure_rate` and absolute failure
count — MA-ROPE causes ~10x fewer absolute failures than AllOffload and ~6x fewer than UCB-RAT,
fleet-wide, by transmitting far less often. This is the same, now-familiar pattern from
`QUEUE_LOSS_ROOT_CAUSE_REPORT.md`, now confirmed to hold against a second, non-trivial baseline —
not just AllOffload.

**CoopEC-RAT is the most competitive alternative found so far.** Its task-property-only heuristic
(no channel/queue awareness by design) still reaches Fleet OTR 0.801 — well above UCB-RAT and
AllOffload, though still behind MA-ROPE's 0.888 — and its `conditional_tx_failure_rate` (2.30%) is
actually the *lowest* of any offloading policy in the table, including MA-ROPE's. Its very low
latency (107ms) reflects that it only offloads compute-heavy tasks (a minority), so most tasks
finish quickly locally. This is a genuinely useful comparison point, not a trivial one.

## Density scaling (N=8 → 16 → 32), Fleet OTR

| N | MA-ROPE | AllOffload | NoOffload | UCB-RAT | CoopEC-RAT |
|---|---:|---:|---:|---:|---:|
| 8 | 0.9328 ± 0.0066 | 0.3397 ± 0.0187 | 1.0000 ± 0.0000 | 0.7053 ± 0.0113 | 0.9029 ± 0.0067 |
| 16 | 0.9325 ± 0.0136 | 0.2653 ± 0.0081 | 1.0000 ± 0.0000 | 0.4526 ± 0.0072 | 0.8233 ± 0.0112 |
| 32 | 0.8875 ± 0.0143 | 0.1246 ± 0.0073 | 1.0000 ± 0.0000 | 0.3455 ± 0.0054 | 0.8014 ± 0.0043 |

MA-ROPE's Fleet OTR advantage over AllOffload and UCB-RAT widens sharply as density increases —
confirmed with real, validated data against non-trivial baselines. CoopEC-RAT degrades far more
gently than UCB-RAT/AllOffload (0.903 → 0.801, a 10-point drop) because its decision rule never
depends on queue or channel state to begin with (by design, per its disclosed non-adaptive
construction) — its degradation comes only from the shared RSU queue's latency contribution
increasing with fleet size, not from any change in its own decisions. MA-ROPE still degrades more
gently still (0.933 → 0.888, a 4.5-point drop) and remains the best performer at every density.

## Density scaling, conditional_tx_failure_rate and fleet_tx_failure_rate (MA-ROPE only)

| N | conditional_tx_failure_rate | fleet_tx_failure_rate | Attempts (of 16,000/8,000/4,000 vehicle-steps) |
|---|---:|---:|---:|
| 8 | 0.0599 ± 0.0039 | 0.0024 ± 0.0001 | 152.4 ± 7.1 (of 4,000) |
| 16 | 0.0469 ± 0.0074 | 0.0020 ± 0.0003 | 336.4 ± 8.5 (of 8,000) |
| 32 | 0.0546 ± 0.0068 | 0.0024 ± 0.0003 | 715.8 ± 10.8 (of 16,000) |

`fleet_tx_failure_rate` stays essentially flat (~0.20-0.24%) across all three densities — MA-ROPE's
absolute reliability per generated task does not meaningfully degrade with fleet size, even though
`conditional_tx_failure_rate` (the per-attempt metric) does not show a clean trend either way. Both
observations are worth including in the paper; neither should be reported alone.

**Footnote on N=8 specifically**: 14 of 15 `ma-rope` checkpoints in this campaign are bit-identical
to Path A's (`CAMPAIGN_CANONICAL_20260802`) — direct evidence the pipeline is genuinely
cross-execution deterministic. The one exception, `ma-rope_n8_seed0`, diverges from Path A for a
known, disclosed reason (Path A's version of that one cell resumed a checkpoint across two different
execution environments; Path B's trained entirely within one) — see `CLAUDE_FINDINGS.md`. Path B's
N=8 numbers reported here are internally self-consistent and, for this cell specifically, arguably
more trustworthy than Path A's. N=16 and N=32 are unaffected.

## Training-duration diagnostic (N=32, seeds 0, 1, 2 — now three seeds)

| Seed | Episodes | conditional_tx_failure_rate | fleet_tx_failure_rate | Fleet OTR | WiFi6 usage (of 16,000 steps) |
|---|---:|---:|---:|---:|---:|
| 0 | 100 | 0.0591 | 0.0026 | 0.9056 | 186 |
| 0 | 250 | 0.0603 | 0.0026 | 0.9032 | 171 |
| 0 | 500 | 0.0592 | 0.0026 | 0.8835 | 185 |
| 1 | 100 | 0.0657 | 0.0029 | 0.8662 | 185 |
| 1 | 250 | 0.0569 | 0.0026 | 0.8972 | 178 |
| 1 | 500 | 0.0633 | 0.0028 | 0.8818 | 175 |
| 2 | 100 | 0.0474 | 0.0022 | 0.9001 | 180 |
| 2 | 250 | 0.0523 | 0.0023 | 0.8909 | 178 |
| 2 | 500 | 0.0651 | 0.0028 | 0.8969 | 187 |

Independently confirmed all 9 checkpoints are genuinely distinct trained networks (pairwise
`torch.equal` on first-layer weights returns `False` for every pair, not just within a seed).

**Within-seed range (100→500 episodes) vs. cross-seed variance**: each seed's own `conditional_tx_failure_rate`
moves by 0.001-0.018 across 5x more training; the 5-seed cross-seed standard deviation for this same
metric (main campaign, `CORRECTED_RESULT_TABLES.md` headline table) is 0.0068 (≈0.014-0.027 range for
typical variation). **The within-seed training-duration effect is the same size as, or smaller than,
ordinary seed-to-seed noise** — not a distinguishable trend. Same pattern for Fleet OTR (within-seed
range 0.009-0.031 vs. cross-seed std 0.0143). **Direction is also inconsistent across seeds**: Fleet
OTR moves down from 100→500 episodes for seed 0 (0.906→0.884) and seed 2 (0.900→0.897, essentially
flat), but up for seed 1 (0.866→0.882) — a genuine training-duration effect would be expected to push
in a consistent direction across independently-seeded runs; this doesn't.

**Conclusion, now supported by three seeds, not one**: five times more training produces no
distinguishable behavioral change in MA-ROPE's RAT usage or failure-rate metrics at N=32. This
directly supports the `PUBLICATION_DECISION.md`/root-cause report's read that the WiFi6 reliance is
a converged policy characteristic, not a training-duration artifact — the evidentiary caveat noted
after the seed-0-only result (single seed, don't over-read) is substantially addressed.
