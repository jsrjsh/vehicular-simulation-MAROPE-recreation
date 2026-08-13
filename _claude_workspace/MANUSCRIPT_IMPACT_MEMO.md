# MANUSCRIPT_IMPACT_MEMO.md

Preliminary memo, per correction-plan item 7. **The manuscript has not been edited.** This assesses
what the Path B correction (metric rename + checkpoint fix) does and does not resolve, and what
remains an open decision once `EXECUTION_CONTRACT_V2.md`'s corrected campaign returns real numbers.
**Do not send any manuscript version to the professor based on this memo alone** — it identifies
what needs to change, it does not yet contain the corrected numbers to put in place of what's there.

## 1. Scope check: what Path B actually fixes

Path B (metric rename, fleet-wide stats, checkpoint persistence) directly addresses exactly one
manuscript claim: the "queue loss" paragraph (`results_part1.tex:175,184,214`, "MA-ROPE 1.15% vs.
AllOffload 2.14%, 1.9x lower"). It does **not** address the broader set of headline-table mismatches
documented in `MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md` §1 — those are a separate, larger problem
that the 7-point correction plan was not scoped to cover. Conflating the two would understate how
much of the manuscript is actually affected, so this memo treats them as two distinct issue classes
below.

## 2. Issue class 1 — the queue-loss claim (Path B's actual target)

**Root cause, established with certainty** (`QUEUE_LOSS_ROOT_CAUSE_REPORT.md` §6, verdict "mixed
causes"): the metric is a link-layer transmission-failure rate conditioned on attempted
transmissions only, not a queue-capacity-rejection rate (no such mechanism exists in the code). Under
that per-attempt denominator, MA-ROPE's rare-but-sometimes-unreliable transmissions (26% land on the
noisier WiFi6 RAT) score worse than AllOffload's constant, always-reliable 5G-NR usage — even though
MA-ROPE causes 11x fewer total failed transmissions fleet-wide (35 vs 385, same 16,000 vehicle-steps,
canonical seed-0 trace).

**What the manuscript currently claims**: "1.9x lower queue loss," framed as an MA-ROPE reliability
advantage, with 1.15%/2.14% as the numbers.

**What's actually true under the corrected metric names** (numbers below are from the *approximated*
forensic trace, not yet the fresh Path B campaign — see §4): under `conditional_tx_failure_rate`
(the renamed old metric), MA-ROPE is *higher* than AllOffload (canonical 5-seed mean 5.46% vs
2.46%). Under `fleet_tx_failure_rate` (failures per all vehicle-steps, the new metric), the
directional story manuscript wants is closer to true: MA-ROPE causes far fewer absolute failures by
transmitting far less often.

**Recommended replacement language** (from the root-cause report, ready to drop in once real
corrected numbers exist): *"MA-ROPE causes N-fold fewer total link failures fleet-wide by minimizing
unnecessary offloading, though its per-attempt reliability trails AllOffload's due to occasional use
of the less reliable WiFi6 link."* This requires reporting **both** `conditional_tx_failure_rate` and
`fleet_tx_failure_rate` side by side, not collapsing to one number — the two metrics tell different,
both-true stories, and picking only one to publish would repeat the same category of error being
corrected here.

**Status**: root cause fully resolved, corrected pipeline built and fidelity-verified, fresh 5-seed
campaign specified in `EXECUTION_CONTRACT_V2.md` but **not yet run**. Manuscript text should not be
touched until that campaign's real numbers are in hand and validated.

## 3. Issue class 2 — the broader headline-table mismatch (NOT addressed by Path B)

`MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md` §1 found that nearly every other headline number at N=32
also disagrees with two independent runs of the current codebase (which agree tightly with each
other, B≈C), categorized mostly **D (different algorithm/behavior)** or **E (different
implementation)**, not noise:

- U_PRR: all three methods off by 14-22% relative, same direction — suggests a systematic
  configuration difference (task mix, reward weighting) between whatever produced the manuscript's
  numbers and the current `V2XEnv`.
- U_OTR: off by 29-84% relative, and the *direction* of the gap is not consistent across methods —
  rules out one scalar miscalibration; points to a genuinely different deadline/utility model.
- Energy: sign-flipped for all three methods (a **previously confirmed, separate defect**: a
  unit-conversion bug mixing `tx_energy_mj` with Joule-scale terms, plus a `log10()`-based formula
  that can go negative — documented in `archive/internal_history/ENERGY_UNIT_IMPACT_REPORT.md`, not
  newly discovered here, and **not fixed by anything in the Path B plan**).
- Latency (AllOffload specifically): off by 369% relative, but B and C match each other almost
  exactly (829.98ms both) — consistent with `archive/internal_history/audits/MAROPE_CALIBRATION_DECISION.md`'s
  note that historical results used "instant, static transmission delays and persistent queues," a
  materially different physical model from what's currently implemented. This is a framing/version
  question, not obviously a "bug" to fix.
- Fleet OTR and Latency for MA-ROPE/NoOffload are comparatively close (Category B, plausible seed
  variance) — not everything is broken, but the MA-ROPE-vs-AllOffload headline comparison, which is
  the paper's central claim, rests on the metrics that diverge most.
- Wu2021: **no implementation exists anywhere in the recovered codebase.** Every Wu2021 number in
  the manuscript is currently unverifiable from any executable artifact.

**This is a materially bigger problem than the queue-loss claim.** It suggests dataset A (the
manuscript's numbers) may come from an earlier, structurally different version of the simulator, not
from typos or seed variance in the current one. Fixing the queue-loss metric name and the checkpoint
gap does nothing to close this gap. **This needs its own Phase 6 path decision** (already flagged as
open in the provenance report, still open here): either (a) treat the current codebase as
authoritative and re-run/re-baseline the entire headline table against it, rewriting the comparative
narrative around whatever the real numbers show, or (b) determine that dataset A came from a
different, documented model version and explicitly scope the paper as reporting on that version
(with the current codebase's numbers presented separately, e.g. as a reproducibility appendix). This
memo does not choose between (a) and (b) — that's a publication-strategy decision, not an engineering
one, and is flagged for explicit discussion rather than decided here.

## 4. What's still pending before any manuscript text can be finalized

- `EXECUTION_CONTRACT_V2.md`'s fresh 5-seed Path B campaign has not been run. The queue-loss numbers
  quoted in §2 above are still the forensic-trace approximation (a ~22% reconstruction gap on
  MA-ROPE specifically, disclosed in the root-cause report) — real, validated numbers require that
  campaign to complete and pass its 11-point checklist.
- The Energy unit-conversion defect (Issue class 2) has no fix plan at all yet — it wasn't part of
  the 7-point correction plan. If (a) from §3 is chosen, this becomes a blocking prerequisite before
  Energy numbers can be reported anywhere.
- Wu2021's status (no implementation) needs an explicit decision: drop it from the comparison table
  entirely (with a note), or treat implementing a faithful Wu2021 baseline as new scope.
- No figures have been regenerated against any corrected data yet (deliberately deferred per
  `EXECUTION_CONTRACT_V2.md` §8).

## 5. Recommendation

Do not edit `results_part1.tex` or any other manuscript file yet. Do not send the current manuscript
to the professor. Once the fresh Path B campaign completes and passes validation, this memo's §2
gets updated with real corrected numbers and the specific queue-loss paragraph rewrite becomes
ready to draft. Separately, and before any submission-quality claim about the paper's headline
results, §3's broader path decision (re-baseline vs. explicitly scope to a documented earlier model
version) needs to be made explicitly — it is the larger and more consequential of the two open
issues, and Path B's completion should not be mistaken for having resolved it.
