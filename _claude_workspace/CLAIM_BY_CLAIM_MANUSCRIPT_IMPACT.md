# CLAIM_BY_CLAIM_MANUSCRIPT_IMPACT.md

Every headline claim in the current manuscript, checked against the validated
`CAMPAIGN_CORRECTED_20260803` data (`CORRECTED_RESULT_TABLES.md`) and the training-duration
diagnostic. Each claim gets one of four verdicts: **KEEP** (defensible as-is), **REVISE** (real
finding, wrong framing/number — replacement provided), **REMOVE** (not defensible, no repair
possible from current data), **UNRESOLVED** (cannot be assessed from anything executed so far).
No manuscript file has been touched — this is the input to that future edit, not the edit itself.

---

## 1. Headline table (N=32, "full_performance")

| Claim | Manuscript says | Corrected finding | Verdict |
|---|---|---|---|
| U_PRR, all 3 methods | MA-ROPE 0.8323, AllOffload 0.7790, NoOffload 0.8442 | MA-ROPE 0.9583±0.0014, AllOffload 0.6076±0.0009, NoOffload 0.9610±0.0008 — all three off by 14-22% relative, same direction | **REVISE.** Real numbers available now (`CORRECTED_RESULT_TABLES.md`); replace the whole row. The *relative ordering* (NoOffload ≥ MA-ROPE > AllOffload) does not match the manuscript's own ordering (AllOffload > NoOffload > MA-ROPE) — this is a reordering, not just a magnitude shift, so this cannot be patched with a caveat; the row needs to be replaced outright. |
| U_OTR, all 3 methods | MA-ROPE 0.7424, AllOffload 0.5644, NoOffload 0.2754 | MA-ROPE 0.5252±0.0016, AllOffload 0.1264±0.0058, NoOffload 0.5079±0.0016 | **REVISE.** Direction of the gap is not uniform across methods (confirmed in `MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md`) — replace the row with real numbers; do not attempt a scaling correction. |
| Fleet OTR, all 3 methods | MA-ROPE 0.8340, AllOffload 0.5250, NoOffload 0.0000 | MA-ROPE 0.8875±0.0143, AllOffload 0.1246±0.0073, NoOffload 1.0000±0.0000 | **REVISE.** MA-ROPE's own number is close (within seed noise); AllOffload and NoOffload are not. NoOffload's 0.0 vs. 1.0 is a definitional convention mismatch, not a computational error (see item 5 below) — needs a footnote, not a number change, once the convention is settled. |
| Energy, all 3 methods | MA-ROPE 0.7057, AllOffload 0.9441, NoOffload 0.5032 | MA-ROPE -1.8144±0.0105, AllOffload 7.1036±0.0095, NoOffload -1.9411±0.0133 | **REMOVE, pending a code fix.** Sign-flipped for all three methods — a confirmed, pre-existing unit-conversion defect (`ENERGY_UNIT_IMPACT_REPORT.md`), not addressed by anything run so far. Do not report Energy numbers in any revised table until this is fixed; this is Tier 1 work still outstanding, not a data-availability problem. |
| Latency, MA-ROPE & NoOffload | MA-ROPE 213.0ms, NoOffload 248.1ms | MA-ROPE 219.67±3.70ms, NoOffload 233.67±3.55ms | **KEEP** (within plausible seed variance, 3.1% and 5.8% relative). |
| Latency, AllOffload | 176.9ms | 829.98±2.21ms | **REVISE, with an explicit scoping note, not a silent number swap.** 369% relative gap, but internally consistent across two independent runs (Path A canonical and now Path B corrected agree to the same value). Reflects RSU queue contention under a physical model the manuscript's number does not appear to include (`MAROPE_CALIBRATION_DECISION.md`'s note about historical "instant, static" delays). The paper needs to state explicitly which physical model is being reported, not just update the number. |
| Wu2021, all metrics | Full row of numbers reported | No verifiable implementation of Wu2021 exists (§4 below) | **REMOVE**, or replace with the UCB-RAT reconstruction, clearly labeled (see §4). |

## 2. Fleet OTR density-scaling narrative (N=8 → 16 → 32)

**Manuscript claim** (implicit in the N=8/16/32 progression and `related_work.tex`'s framing):
MA-ROPE's Fleet OTR advantage over AllOffload widens as fleet density grows.

**Corrected finding**: confirmed, and now backed by a second non-trivial baseline. MA-ROPE: 0.933 →
0.933 → 0.888 (N=8/16/32, a 4.5-point drop). AllOffload: 0.340 → 0.265 → 0.125 (59-point drop).
UCB-RAT: 0.705 → 0.453 → 0.346 (36-point drop). MA-ROPE's advantage over *both* alternatives widens
substantially with density.

**Verdict: KEEP, and strengthen.** This is the one part of the original narrative that survives
contact with the real data, and it's now more evidenced than before (a second baseline confirms the
same pattern, not just one). Recommend leading the results section with this claim rather than the
queue-loss claim.

## 3. Queue-loss claim ("1.9x lower queue loss: MA-ROPE 1.15% vs. AllOffload 2.14%")

**Corrected finding**, now with real (not forensic-approximation) Path B numbers:
`conditional_tx_failure_rate` MA-ROPE 5.46%±0.68% vs. AllOffload 2.46%±0.08% — reversed from the
manuscript's claimed direction. `fleet_tx_failure_rate` (the denominator that counts every generated
task, not just attempted ones) MA-ROPE 0.24%±0.03% vs. AllOffload 2.46%±0.08% — MA-ROPE now
decisively *ahead*, by about 10x. Absolute fleet-wide failures: 39.2 vs. 393.8 over the same
16,000-vehicle-step evaluation.

**Verdict: REMOVE the original claim, REVISE with the full two-metric picture.** Do not report
either number alone — report both, with the mechanism (`QUEUE_LOSS_ROOT_CAUSE_REPORT.md`): MA-ROPE
transmits far less often, so its rare failures are a large fraction of a small attempt count
(inflating the per-attempt rate) while being a tiny fraction of all generated tasks (deflating the
fleet-wide rate). Suggested replacement language: *"MA-ROPE reduces fleet-wide transmission failures
by roughly 10x relative to AllOffload (0.24% vs. 2.46% of all generated tasks) by minimizing
unnecessary offloading; its conditional failure rate on the attempts it does make is higher (5.46%
vs. 2.46%), reflecting occasional use of the less reliable WiFi-6 link."* Never rename this back to
"queue loss" — no queue-capacity-rejection mechanism exists in the simulator (§1 of the root-cause
report).

## 4. Wu2021 baseline

**Manuscript claim**: Wu2021 (UCB Bandit) achieves specific U_PRR/U_OTR/Fleet-OTR/Energy/Latency
values (`results_part1.tex` line 16), compared directly against MA-ROPE.

**Corrected finding**: no verifiable implementation of Wu2021 exists anywhere in the recovered
codebase, and the manuscript's own citation provides no equations or hyperparameters to reconstruct
one faithfully. A disclosed, non-certified reconstruction (UCB-RAT, `EXECUTION_CONTRACT_V3.md` §0)
was built and run instead: at N=32, U_PRR 0.899±0.002, Fleet OTR 0.346±0.005,
`conditional_tx_failure_rate` 2.54%±0.08%, `fleet_tx_failure_rate` 1.41%±0.04% — MA-ROPE beats it on
every metric except the conditional rate, for the same disclosed reason as §3.

**Verdict: REMOVE the Wu2021 row as currently written; REVISE by substituting the UCB-RAT
reconstruction, labeled honestly.** The table row must read "UCB-RAT (Wu2021-inspired
reconstruction)" — never "Wu2021" unqualified — with a footnote explaining it is not a certified
reproduction. This is more defensible than either keeping unverifiable numbers or having no
non-trivial comparator at all.

**Escalated finding, now resolved by decision**: investigating the other four named baselines
(MADDPG, CoopEC-Shao2025, Lyapunov-Jing2019, GA+DQN-Yun2022) surfaced that the manuscript's own
headline table shows 10 of 12 rows sharing an identical Fleet OTR value to 4 decimal places,
including MA-ROPE's own row — see `BASELINE_TABLE_INTEGRITY_FINDING.md`. There was no credible
target to "reproduce" for any of the four. **Decision made**: `coopec_greedy` was implemented as a
genuinely new baseline ("CoopEC-RAT," a disclosed reconstruction, not a reproduction — see
`CORRECTED_RESULT_TABLES.md`); it is the most competitive alternative found so far (Fleet OTR 0.801
at N=32, lowest `conditional_tx_failure_rate` of any offloading policy). MADDPG and
GA+DQN-Yun2022 are **REMOVE** — dropped from the comparison table entirely, with a disclosed note.
Lyapunov-Jing2019 is **queued as future work**, not implemented this round.

## 5. NoOffload's Fleet OTR (0.0 in the manuscript vs. 1.0 in the current code)

**Corrected finding**: traced to one line — `evaluate_policy()`'s default-value convention returns
1.0 when no transmission was ever attempted, since NoOffload's `tx_on_times` list is always empty.
Not a computational bug.

**Verdict: REVISE via an explicit definitional footnote, not a number change.** Either keep the
code's 1.0 convention and footnote why NoOffload trivially satisfies its own (non-existent) V2X
deadline, or override the convention to report 0.0 for this one edge case with the override
disclosed in the text. This is a decision, not a fix — flagging it rather than picking one silently.

## 6. Training-duration diagnostic — informs the Path B vs. Path C decision, not a manuscript claim yet

**Finding**: five times more training (100→500 episodes) produces no material change in MA-ROPE's
RAT-usage distribution or failure-rate metrics at N=32, seed=0 (`CORRECTED_RESULT_TABLES.md`).
Independently confirmed the checkpoints are genuinely different trained networks, ruling out a
stalled-resume artifact.

**Verdict: Supports, but does not yet settle, "Path B not Path C."** Single seed — per
`EXECUTION_CONTRACT_V3.md` §3, expanding to 2-3 more seeds before treating this as closed is the
recommended next step, not an automatic conclusion. Not a claim to put in the manuscript yet either
way.

---

## Summary count

| Verdict | Count |
|---|---|
| KEEP | 2 (Latency for MA-ROPE/NoOffload; Fleet OTR density-scaling narrative, now strengthened by two non-trivial baselines) |
| REVISE | 5 (U_PRR row, U_OTR row, Fleet OTR row, Latency-AllOffload with scoping note, queue-loss claim) |
| REMOVE | 3 (Energy — blocked on a formula defect, not just a units issue; Wu2021 row — replaced by CoopEC/UCB-RAT reconstructions; MADDPG and GA+DQN-Yun2022 rows — dropped, no credible target) |
| RESOLVED BY DECISION | 1 (baseline scope: CoopEC-RAT implemented as new work, Lyapunov-Jing2019 queued for future work) |

**Net read**: roughly half the headline table survives with real numbers substituted in; Energy
cannot be reported at all — the defect turned out to be a dimensionally invalid formula, not a fixable
units mismatch; the queue-loss claim needs a full reframe (not a number swap); and the comparison
table now has two genuinely-implemented, honestly-labeled non-trivial baselines (UCB-RAT, CoopEC-RAT)
in place of the four originally-cited ones, three of which showed no credible target to reproduce
against at all.
