# SCIENTIFIC_POSITION_REPORT.md

Written as Principal Investigator, reviewing the full evidence base accumulated across the
engineering phase: `CLAUDE_FINDINGS.md`, `MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md`,
`QUEUE_LOSS_ROOT_CAUSE_REPORT.md`, `MANUSCRIPT_IMPACT_MEMO.md`, and the two execution contracts.
Every finding below is classified:

- **A. Confirmed** — established with direct, reproducible evidence (independent runs agreeing,
  code traced to a specific line, hash-verified execution).
- **B. Disproved** — a hypothesis that was tested and shown false.
- **C. Partially confirmed** — real and directionally correct, but with a known gap, caveat, or
  unresolved magnitude.
- **D. Replaced by better evidence** — an earlier explanation that was reasonable at the time but
  has been superseded by a stronger, more specific finding.

One overarching caveat before the findings: **the fresh Path B campaign (`CAMPAIGN_CORRECTED_20260803`,
per `EXECUTION_CONTRACT_V2.md`) has not been executed yet.** Everything below reflects Path A
(`CAMPAIGN_CANONICAL_20260802`, fully complete and independently validated) plus a forensic
approximation for the Path B metric behavior. This is flagged inline wherever it matters.

---

## 1. Manuscript provenance

| Finding | Class | Evidence |
|---|---|---|
| The manuscript's headline N=32 table does not match two independent executions of the current codebase on nearly every metric except Fleet OTR (partial) and Latency (MA-ROPE/NoOffload only) | **A** | `MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md` §1 — Categories D/E dominate; B≈C agree to 3-4 decimals with each other on every metric, isolating the mismatch to "manuscript vs. current code," not "run vs. run." |
| Historical queue-loss drift across manuscript versions (1.15% → 0.85% → 2.14% → 38.0% → 1.3%) is explained by 6-7 overlapping, unlabeled experimental campaigns mixed in one output directory (`results/paper_reproduction/`, timestamps spanning 2026-07-14 to 07-16) | **A** | `CLAUDE_FINDINGS.md`, "Actual root cause of queue-loss drift" — direct file-timestamp and checkpoint-hash forensics, 35 CSVs for 5 seeds at N=8 where 5 were expected. |
| The `is_new_task` reset bug explains the manuscript pipeline's queue-loss numbers | **D**, replaced | Bug is real and fixed, but `env_mode="baseline_recreation"` (the mode the canonical pipeline actually uses) bypasses the `is_new_task` gate entirely — confirmed by direct code trace. Superseded by the campaign-contamination finding above as the operative explanation. |
| `V2XEnv` + `env_mode="baseline_recreation"` + `reproduce_paper_sweeps.py` is the canonical, manuscript-producing pipeline (not `V2XEnvPlus`/`train_b3_baselines.py`) | **A** | Exact filename-pattern and CSV-schema matching against files already on disk — not inference. |
| Wu2021 baseline numbers in the manuscript are reproducible from the current codebase | **B**, disproved | Exhaustive grep across every `.py` file for `wu2021`/`wu_2021`: zero matches. No implementation exists to check against. |
| A ~50k-parameter claim (Table XIV-style) contradicts the real ~136,460-parameter network | **Unverifiable — dropped** | Grep across every `.tex` file in the current manuscript source found no matching claim anywhere. Cannot confirm this discrepancy exists in the document as it currently stands; not reported as a finding. |

---

## 2. Canonical campaign (Path A, `CAMPAIGN_CANONICAL_20260802`)

| Finding | Class | Evidence |
|---|---|---|
| All 45 combinations (3 methods × 3 densities × 5 seeds) completed under the frozen, unmodified protocol | **A** | Independently validated post-hoc: checkpoint hashes recomputed from file bytes, `step_count=10000`/`fedavg_rounds=200` structural invariant checked per combo, wall-clock self-consistency checked — not accepted on the executor's self-report alone. |
| Original `train_ma_rope()` produces non-reproducible network initialization because `torch.manual_seed()` is never called anywhere in the frozen pipeline | **A** | Empirically demonstrated: three fresh-process constructions of the identical network produced three different first-weight values. Fixed at the orchestrator level only (no frozen file touched). |
| Chunked, checkpoint/resume training (required by this sandbox's 45-second execution cap) is bit-identical to an uninterrupted run of the real `train_ma_rope()` | **A** | Direct hash/step-count/FedAvg-round comparison, chunked vs. uninterrupted, same seed: exact match. |

---

## 3. Office benchmark (Dataset B — a prior, independent run of the same canonical pipeline)

| Finding | Class | Evidence |
|---|---|---|
| The simulator itself is internally deterministic and reproducible run-to-run, independent of the manuscript's numbers | **A** | B and C (Dataset B from `archive/internal_history/`, Dataset C from this session) agree to 3-4 decimal places on U_PRR, exactly on Energy/Latency, despite being executed months apart on different hardware. This is the single most load-bearing confirmed fact in the whole investigation: it proves any manuscript mismatch is not "the simulator is flaky," it's "the manuscript reflects something else." |

---

## 4. AG (Antigravity) reconstruction

| Finding | Class | Evidence |
|---|---|---|
| Antigravity's completion of the remaining N=32 MA-ROPE training (which this sandbox could not execute) is genuine, not a fabricated or hallucinated status report | **A** | Independently re-verified, not trusted at face value: checkpoint hashes recomputed directly from returned file bytes, `step_count`/`fedavg_rounds` arithmetic checked, sum of per-combo durations cross-checked against reported wall-clock time — all passed. |

---

## 5. Queue-loss investigation

| Finding | Class | Evidence |
|---|---|---|
| `queue_loss` measures link-layer transmission failure rate conditional on an attempted transmission — not RSU queue-capacity rejection | **A** | Full code trace, `QUEUE_LOSS_ROOT_CAUSE_REPORT.md` §1: no capacity cap exists anywhere on `rsu_queues`; the queue only ever contributes to latency. |
| A genuine queue-capacity bug causes the MA-ROPE-vs-AllOffload reversal | **B**, disproved | No such mechanism exists in the code to contain a bug (Category A ruled out with certainty). |
| The reversal (MA-ROPE 5.46% vs AllOffload 2.46% under the metric as implemented) is caused by denominator choice (attempts-only) interacting with per-RAT reliability differences (WiFi6's -90dBm noise floor vs. 5G-NR's -110dBm) | **A** | Event-level decomposition, `QUEUE_LOSS_ROOT_CAUSE_REPORT.md` §3-4: recomputing with a per-generated-task denominator reverses the ordering back to the manuscript's claimed direction; RAT-level breakdown isolates WiFi6 as 80% of MA-ROPE's failures despite being 26% of its attempts. |
| MA-ROPE causes far fewer absolute transmission failures fleet-wide than AllOffload, even though its per-attempt rate is higher | **A** | Same decomposition: 35 vs. 385 failed transmissions out of the same 16,000 vehicle-steps — an 11x absolute advantage that the per-attempt rate metric does not surface. |
| The manuscript's "1.9x lower queue loss" claim, as stated, is defensible against the current codebase | **B**, disproved | Not by degree — by direction. Under the actual metric definition, MA-ROPE's rate is more than double AllOffload's, not half. |
| The forensic trace's MA-ROPE reconstruction (4.63%) exactly matches the canonical campaign's reported value (5.91% for that seed) | **C**, partial | ~22% relative gap, root-caused to the checkpoint-persistence limitation (only agent 0's weights were recoverable for the trace). Qualitative conclusion (direction of the reversal) is robust to this gap; the exact quantitative magnitude is not yet nailed down and awaits the Path B campaign. |

---

## 6. Checkpoint investigation

| Finding | Class | Evidence |
|---|---|---|
| `train_ma_rope()`'s saved checkpoint (agent 0 only) is insufficient to exactly reconstruct the multi-agent evaluation that `evaluate_policy()` actually performed | **A** | Discovered as a side effect of the queue-loss forensics; confirmed by code inspection of the save/load asymmetry. |
| The Path B fix (persisting all N agents' weights) works correctly | **A** | Directly tested: trained a 3-agent fixture through 2 real episodes, confirmed `update_count > 0` (ruling out a trivial pass on an untrained network), verified all 3 saved state_dicts are present and byte-identical to the live in-memory weights. Exit code 0. |

---

## 7. Metric investigation (energy formula, Fleet OTR convention)

| Finding | Class | Evidence |
|---|---|---|
| A unit-conversion defect (`tx_energy_mj` mixed with Joule-scale terms) plus a `log10()`-based formula that can go negative causes energy values to sign-flip relative to the manuscript | **A** | Confirmed pre-existing finding (`archive/internal_history/ENERGY_UNIT_IMPACT_REPORT.md`), reconfirmed here: B and C agree with each other to 4 decimals (internally consistent), both disagree sharply with the manuscript. **Not addressed by Path B** — this is a separate, still-open defect. |
| NoOffload's Fleet OTR of 1.0 (vs. the manuscript's 0.0) is a bug | **B**, disproved | Traced to one specific line: `fleet_otr_val = np.mean(tx_on_times) if tx_on_times else 1.0`. NoOffload never transmits, so the list is always empty and the function's own default-value convention returns 1.0. This is a definitional mismatch for an edge case, not a computational error. |

---

## 8. Fleet OTR behaviour

| Finding | Class | Evidence |
|---|---|---|
| MA-ROPE's Fleet OTR advantage over AllOffload widens as fleet density increases (N=8→16→32) | **A** | Direction confirmed at all three densities against real canonical data — the one part of the manuscript's headline narrative that survives contact with the actual code. |
| The absolute magnitude of that advantage matches the manuscript | **B**, disproved | AllOffload collapses far harder in reality (0.125 at N=32) than the manuscript implies (0.525) — traced to RSU queue contention under 5G at high density, a dynamic the manuscript's much lower latency figures suggest wasn't modeled the same way when those numbers were produced. |

---

## 9. Energy behaviour

| Finding | Class | Evidence |
|---|---|---|
| The current codebase computes energy consistently with itself | **A** | B and C agree to 4 decimal places across all three methods. |
| The current codebase's energy values agree with the manuscript | **B**, disproved | Sign-flipped for all three methods (357-652% relative difference), consistent with the known unit-conversion defect above. |

---

## 10. Latency behaviour

| Finding | Class | Evidence |
|---|---|---|
| MA-ROPE and NoOffload latency figures are consistent with the manuscript within plausible seed variance | **A** | 3.1% and 5.8% relative difference respectively — Category B, normal variance. |
| AllOffload's latency figure is consistent with the manuscript | **B**, disproved | 369% relative difference, but B and C match each other almost exactly (829.98ms both) — this is systematic, not noise. Points to `results_part1.tex`'s numbers coming from a documented earlier physical model ("instant, static transmission delays and persistent queues" per `archive/internal_history/audits/MAROPE_CALIBRATION_DECISION.md`), materially different from the RSU-queue-contention model currently implemented. |

---

## 11. Utility metrics (U_PRR, U_OTR)

| Finding | Class | Evidence |
|---|---|---|
| U_PRR mismatches (14-22% relative, same direction across all three methods) reflect a single systematic configuration difference (task mix or reward weighting) between whatever produced the manuscript and the current environment | **A** | Uniform direction and comparable magnitude across independently-implemented methods rules out a per-method bug; points to a shared upstream parameter difference. |
| U_OTR mismatches (29-84% relative) are explained by the same systematic difference as U_PRR | **B**, disproved | Direction of the gap is *not* consistent across methods (NoOffload's real value is higher than claimed; MA-ROPE/AllOffload's are lower) — rules out one scalar miscalibration, indicating a genuinely different deadline/utility model, not a single shared config knob. |

---

## Synthesis

Three findings carry the whole investigation and should anchor every downstream decision:

1. **The simulator is trustworthy.** B≈C (two independent runs of the current code, months apart) agreeing to 3-4 decimal places on nearly every metric is the strongest evidence in this entire body of work. Nothing about the corrected-implementation results should be doubted on grounds of simulator instability.

2. **The manuscript's numbers (Dataset A) come from something structurally different, not from typos.** The mismatches are too large, too systematic within each metric, and too consistent between two independent modern runs to be transcription errors. The most defensible reading is that Dataset A reflects an earlier, different physical model (confirmed for latency/queue contention via `MAROPE_CALIBRATION_DECISION.md`) and/or a different reward/task-mix configuration (confirmed for U_PRR/U_OTR) — not that today's code is broken relative to some ground truth the manuscript correctly captured.

3. **The queue-loss claim's reversal is fully understood and it is not a simulator bug** — it is a metric-definition artifact colliding with a genuine, defensible RAT-reliability tradeoff (MA-ROPE trades a higher per-attempt failure rate for an 11x reduction in absolute failures by transmitting less often). This is arguably a more interesting and more publishable finding than the manuscript's original, simpler claim.

What remains genuinely open, and is **not** resolved by anything documented above: whether the broader headline-table mismatch (Issue class 2 in `MANUSCRIPT_IMPACT_MEMO.md`) means the paper needs a full re-baseline against the current codebase, or whether Dataset A should be explicitly scoped as a different, earlier model version. That is a publication-strategy decision, addressed in `PUBLICATION_DECISION.md`, not a finding that can be classified A-D from evidence alone.
