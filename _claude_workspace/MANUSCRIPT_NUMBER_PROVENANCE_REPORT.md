# MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md

Every headline number in the manuscript's Table "full_performance" (N=32 primary comparison),
the fleet-OTR scaling story, and the queue-loss claim, traced against three independent
executions of related pipelines. No number here is estimated or interpolated — every cell is
either a manuscript quote (with line number) or a value read directly from a named CSV/JSON file
already on disk.

## Datasets

**A — Manuscript.** `MA_ROPE/MASTER/MA_ROPE_MASTER_v21/sections/results_part1.tex`, table
`full_performance` (lines 9-27) and the fleet-scaling discussion (lines 160-214). This is the
current, live manuscript text — verified via direct grep, not memory.

**B — Office benchmark.** `archive/internal_history/N32_REPRODUCTION_REPORT.md` and
`N8_REPRODUCTION_REPORT.md`. These are literal outputs of `reproduce_paper_sweeps.py`'s own
`generate_reports()` function (confirmed by matching its hardcoded table structure and target
values against the function's source) — i.e. a **prior run of the same canonical pipeline**,
executed before this session, timestamped July 16 in the archive.

**C — Canonical campaign (this session).** `results/CAMPAIGN_CANONICAL_20260802/CANONICAL_BASELINE_RESULTS.csv`,
45/45 combinations, independently validated (see `EXECUTION_CONTRACT.md` §9). Same pipeline as B
(`reproduce_paper_sweeps.py`, `V2XEnv`, `baseline_recreation`), executed independently on
different hardware, months apart.

**D — Prior "4A" reconstruction.** `results/phase4a7/aggregate.json` and
`results/phase4a8/aggregate.json`. **Important caveat, not glossed over**: this dataset was
produced by a *different* evaluation script (`evaluate_phase4a7.py`/`evaluate_phase4a8.py`), which
also imports `env/environment.py:V2XEnv` but computes metrics its own way and additionally sweeps
a `local_reliability_mode` parameter (`local_success`/`local_neutral`/`local_default`) that has no
equivalent in `reproduce_paper_sweeps.py`. It is **not directly numerically comparable** to A/B/C
on a cell-by-cell basis — it's included where it corroborates or adds context, always labeled.

## Category taxonomy (used below exactly as specified)

A. Perfect reproduction — B. Statistical variance — C. Different configuration — D. Different
algorithm — E. Different implementation — F. Possible manuscript transcription error — G. Unknown

---

## 1. Headline Table (N=32, "full_performance")

| Metric | Method | A: Manuscript | B: Office (prior run) | C: Canonical (this session) | Abs diff (A vs C) | Rel diff (A vs C) | Category | Evidence |
|---|---|---:|---:|---:|---:|---:|---|---|
| U_PRR | MA-ROPE | 0.8323 | 0.9571 | 0.9583 ± 0.0014 | 0.1260 | 15.1% | **E** | B and C agree to 3 decimals across independent runs (proves the *simulator* is stable); A is the outlier. `results_part1.tex:14`; `N32_REPRODUCTION_REPORT.md:11`; `CANONICAL_BASELINE_RESULTS.csv` rows `ma-rope,32,*`. |
| U_PRR | AllOffload | 0.7790 | 0.6076 | 0.6076 ± 0.0009 | 0.1714 | 22.0% | **E** | B and C match to 4 decimals exactly. `results_part1.tex:24`; `N32_REPRODUCTION_REPORT.md:16`. |
| U_PRR | NoOffload | 0.8442 | 0.9610 | 0.9610 ± 0.0008 | 0.1168 | 13.8% | **E** | Same pattern: all three methods shift in the same direction and by a similar margin relative to A, which points to a systematic difference in reward/task-mix configuration between whatever produced A and the current `V2XEnv`, not a method-specific bug. `results_part1.tex:25`. |
| U_OTR | MA-ROPE | 0.7424 | 0.5241 | 0.5252 ± 0.0016 | 0.2172 | 29.3% | **D** | B/C agree; direction of the A-vs-C gap is *not* uniform across methods (see next two rows), ruling out a single scalar miscalibration. |
| U_OTR | AllOffload | 0.5644 | 0.1264 | 0.1264 ± 0.0058 | 0.4380 | 77.6% | **D** | Real AllOffload's U_OTR collapses under RSU queue contention at N=32 (see Latency row) — a dynamic the manuscript's number does not reflect. |
| U_OTR | NoOffload | 0.2754 | 0.5079 | 0.5079 ± 0.0016 | 0.2325 | 84.4% | **D** | Goes the *opposite* direction from MA-ROPE/AllOffload (real value is higher than claimed, not lower) — direct evidence this isn't one uniform bug but a genuinely different deadline/utility model. |
| Fleet OTR | MA-ROPE | 0.8340 | 0.8882 | 0.8875 ± 0.0143 | 0.0535 | 6.4% | **B** | Closest metric in the table; within plausible seed variance given the ~1.4% std across seeds. |
| Fleet OTR | AllOffload | 0.5250 | 0.1246 | 0.1246 ± 0.0073 | 0.4004 | 76.3% | **D** | See Latency row — AllOffload's real fleet OTR collapses because of RSU queue delay at N=32, a mechanism the manuscript's static/lower latency figure implies wasn't modeled the same way when A was produced. |
| Fleet OTR | NoOffload | 0.0000 | 1.0000 | 1.0000 ± 0.0000 | 1.0000 | n/a (0 in denominator) | **E — code-level, fully explained** | `evaluate_policy()` in `scripts/reproduce_paper_sweeps.py` line 217: `fleet_otr_val = np.mean(tx_on_times) if tx_on_times else 1.0`. NoOffload never transmits, so `tx_on_times` is always empty and the function *defaults to 1.0* by convention. The manuscript instead defines NoOffload's fleet OTR as 0 (no V2X delivery occurs at all). This is a definitional/convention mismatch for a zero-denominator case, not a training or physics discrepancy — precisely locatable to one line of code. |
| Energy (J) | MA-ROPE | 0.7057 | -1.8090 | -1.8144 ± 0.0105 | 2.5201 | 357% (sign flip) | **E** | Confirmed pre-existing finding, not new: `archive/internal_history/ENERGY_UNIT_IMPACT_REPORT.md` documents a confirmed unit-conversion defect (`tx_energy_mj` mixed with Joule-scale terms) plus a literal `math.log10()`-based energy formula in `env/environment.py`'s `baseline_recreation` branch that can go negative. B and C agree almost exactly, confirming the *current* code is internally consistent — it just doesn't compute energy the way A implies. |
| Energy (J) | AllOffload | 0.9441 | 7.1036 | 7.1036 ± 0.0095 | 6.1595 | 652% | **E** | Same root cause as above; B/C match to 4 decimals. |
| Energy (J) | NoOffload | 0.5032 | -1.9411 | -1.9411 ± 0.0133 | 2.4443 | 486% | **E** | Same root cause. |
| Latency (ms) | MA-ROPE | 213.0 | 222.93 | 219.67 ± 3.70 | 6.67 | 3.1% | **B** | Within normal seed variance. |
| Latency (ms) | AllOffload | 176.9 | 829.98 | 829.98 ± 2.21 | 653.08 | 369% | **D** | B and C match almost exactly (829.98 both times) — this is not noise. At N=32, every vehicle fully offloading via 5G saturates the RSU queue (`l_queue = rsu_queues[idx] * delay_per_unit_ms` in `env/environment.py`'s `step()`); the manuscript's much lower figure implies AllOffload was evaluated under a different or absent queue-contention model when A was produced — consistent with `archive/internal_history/audits/MAROPE_CALIBRATION_DECISION.md` Part 4's explicit note that historical results used "instant, static transmission delays and persistent queues," a materially different physical model from the one currently implemented. |
| Latency (ms) | NoOffload | 248.1 | 233.67 | 233.67 ± 3.55 | 14.43 | 5.8% | **B** | Borderline but plausibly seed variance. |
| Wu2021 (all metrics) | — | 0.8268 / 0.7437 / 0.8340 / 0.7221 J / 204.0 | n/a | n/a | n/a | n/a | **G — Unknown, cannot be resolved from code** | No Wu2021 implementation exists anywhere in the recovered codebase (exhaustive grep, zero matches — see `EXECUTION_CONTRACT.md` §4). These numbers cannot be traced to any executable artifact. Not fabricated here; simply absent. |

## 2. Fleet OTR scaling story (N=8 → N=16 → N=32)

| N | Method | A: Manuscript | C: Canonical | Ordering preserved? |
|---|---|---:|---:|---|
| 8  | MA-ROPE   | 0.887 | 0.9297 ± 0.0055 | — |
| 8  | AllOffload| 0.877 | 0.3397 ± 0.0187 | MA-ROPE > AllOffload in both (✓ direction), gap much larger in reality |
| 16 | MA-ROPE   | 0.869 | 0.9325 ± 0.0136 | — |
| 16 | AllOffload| 0.757 | 0.2653 ± 0.0081 | ✓ direction preserved, gap larger in reality |
| 32 | MA-ROPE   | 0.834 | 0.8875 ± 0.0143 | — |
| 32 | AllOffload| 0.525 | 0.1246 ± 0.0073 | ✓ direction preserved, gap larger in reality |

**Category: B/D mixed.** The *qualitative* claim — "MA-ROPE's fleet OTR advantage over AllOffload
widens as fleet size grows" — is directionally supported by the real simulator; the magnitude is
not (AllOffload collapses far harder in reality than claimed, per the Latency/queue finding
above). This is the one part of the headline narrative that survives contact with the actual code,
even though the absolute numbers don't match.

## 3. Queue loss claim — the most consequential finding in this report

Manuscript (`results_part1.tex:175`, `:184`, `:214`): **"Queue loss @ N=32: MA-ROPE 1.15% vs.
AllOffload 2.14%, 1.9x lower."** This is presented as a supporting pillar of "why MA-ROPE wins."

Real data, both independent runs (B and C):

| Method | A: Manuscript | C: Canonical (mean ± std, 5 seeds) |
|---|---:|---:|
| MA-ROPE | 1.15% | **5.46% ± 0.68%** |
| AllOffload | 2.14% | 2.46% ± 0.08% |

**AllOffload's number is close (2.46% vs 2.14%, 15% relative — plausibly category B).
MA-ROPE's is not close, and the ordering is reversed: in the actual canonical simulator, MA-ROPE's
queue loss is more than double AllOffload's, not half of it.** This directly contradicts the
manuscript's "1.9x lower" claim — not by degree, but by direction. category: **D — different
algorithm/behavior**, not a rounding or config issue. This is consistent with (not caused by) the
`is_new_task` reset bug documented earlier in `CLAUDE_FINDINGS.md`, which was shown to *not*
apply to `baseline_recreation` mode — so that bug is not the explanation here. The actual
mechanism has not yet been isolated; it requires a dedicated controlled experiment (Phase 4
continuation) rather than further speculation in this report.

## 4. What this report does not resolve

- Root cause of the queue-loss reversal (flagged above as the next concrete investigation, not
  guessed at here).
- Wu2021's numbers (Category G, unresolvable without a real implementation).
- Whether Dataset A's numbers came from a materially different, earlier version of the simulator
  (static/instant transmission per `MAROPE_CALIBRATION_DECISION.md`), or from hand-edited/manually
  adjusted values. The evidence (B≈C reproducibility, A systematically different across nearly
  every metric) is most consistent with "different implementation/physical model" (Category
  D/E) rather than a handful of transcription slips (Category F) — the discrepancies are too
  large, too systematic, and too consistent between two independent runs of the current code to
  be simple typos.

## 5. Recommendation

Per the working rules ("prefer weaker but reproducible results over stronger unsupported
results"), the headline Table and the queue-loss claim as currently written are not defensible
against the actual codebase. The Fleet-OTR *directional* story is the one claim that survives.
This supports moving to Phase 6 (choose Path B: corrected MA-ROPE, or Path C: MA-ROPE++) rather
than attempting to further "fix" the manuscript's existing numbers into agreement — the gap is
structural, not cosmetic.
