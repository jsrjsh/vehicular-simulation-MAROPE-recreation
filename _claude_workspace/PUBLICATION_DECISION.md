# PUBLICATION_DECISION.md

PI-level judgment on publishability, minimum required work, and which paper this becomes. Written
against `SCIENTIFIC_POSITION_REPORT.md`'s classified findings — nothing here restates evidence
already established there.

---

## 1. Editor verdict: would I accept this, blind to the historical manuscript?

Reading only what the corrected canonical implementation can currently support, evaluated against
each axis an IEEE TVT Associate Editor would actually use:

| Axis | Assessment |
|---|---|
| **Novelty** | Incremental, not groundbreaking. Federated multi-agent D3QN + PER for heterogeneous V2X RAT/offload-ratio selection is a reasonable combination but sits in an increasingly crowded FL-for-V2X-offloading space by 2026. The dual-utility (U_PRR/U_OTR) formulation and the LDP privacy layer add some distinctiveness. Not, by itself, enough novelty to carry a weak experimental section. |
| **Technical correctness** | Mixed, and currently unresolved. The queue-loss metric — the one thing rigorously re-examined here — is now correctly understood and correctly named. But three other headline metrics (U_PRR, U_OTR, Energy) have *not* been corrected, only diagnosed (Category D/E mismatch vs. the manuscript, root cause not yet fixed for Energy, not yet decided for U_PRR/U_OTR). A paper cannot claim "corrected" results while three of six headline metrics are still an open question. |
| **Reproducibility** | A genuine strength, unusual for this subfield. Exact seeds, checkpoint hashing, fidelity-verified checkpoint/resume, full campaign provenance manifests, independent hash-based validation rather than trusting self-reported completion. If anything in this submission is publication-ready today, it's the reproducibility infrastructure. |
| **Methodology** | The algorithm (D3QN+PER+FedAvg+Gaussian LDP) is appropriately matched to the stated problem; FedAvg's participation-threshold-abort behavior is a sound design choice. No methodological red flags at the algorithm level. |
| **Experimental design** | **The weakest axis.** The comparison set is MA-ROPE vs. two trivial policies (AllOffload, NoOffload) — no other RL-based or heuristic baseline exists in the recovered codebase (Wu2021, the one comparator that would have supplied this, has no implementation anywhere). A reviewer will immediately ask "beats what, exactly?" Beating "always offload everything" and "never offload anything" is a low bar; it does not establish that MA-ROPE is competitive with the state of the art. |
| **Engineering contribution** | Solid, workmanlike systems engineering (federated coordination, privacy layer, multi-RAT action space). Not itself a headline contribution for a TVT algorithms/systems paper. |
| **Practical impact** | Real and well-motivated: heterogeneous RAT selection under a privacy constraint is a genuine deployment concern for connected vehicles. This is the paper's best qualitative selling point, if the numbers back it up. |

**Verdict: Not currently publishable at IEEE TVT in its present state.** Reject, not because the
underlying idea is unsound, but because (a) the corrected campaign that would produce trustworthy
numbers has not been run yet, (b) three of six headline metrics remain uncorrected/undecided, and
(c) the experimental design lacks any non-trivial baseline, which is disqualifying on its own
regardless of how clean the numbers end up being.

**Conditional verdict**: if Tier 1 work (below) is completed, this becomes a plausible **Major
Revision → Accept** candidate at IEEE TVT or a comparable mid-tier venue — not a top-tier flagship
submission, given the novelty ceiling, but a legitimate, honestly-reported systems paper. The
strongest path to a more compelling submission is not polishing the existing claim but reframing
around the more interesting finding this investigation actually produced: a real, evidenced
reliability/absolute-failure-count tradeoff (see `RESEARCH_ROADMAP.md`), which is a more nuanced
and more defensible contribution than the original flat "1.9x lower queue loss" claim.

---

## 2. Minimum scientific work required for publication quality

Scientific work only — no software engineering, refactoring, or infrastructure cleanup. Everything
below assumes the engineering infrastructure (campaign runner, checkpoint fixes, provenance
manifests) is already sufficient, which it is.

### Tier 1 — must complete before professor review

1. **Run the fresh Path B campaign** (`CAMPAIGN_CORRECTED_20260803`, per `EXECUTION_CONTRACT_V2.md`)
   and validate it against the 11-point checklist. Every corrected number currently in hand is a
   forensic-trace *approximation* with a disclosed ~22% reconstruction gap on MA-ROPE specifically —
   not something to show a professor as final.
2. **Make the Issue-class-2 decision explicitly**: either re-baseline the entire headline table
   against the current codebase (treating Dataset A as obsolete), or explicitly scope the paper to
   a documented earlier model version and present current-code numbers as a reproducibility
   appendix. This is a publication-strategy call, not something that resolves itself — it has to be
   made, in writing, before a single manuscript sentence is rewritten.
3. **Resolve the energy metric.** The unit-conversion/sign-flip defect is a real, uncorrected code
   issue, independent of the queue-loss work. Depending on the Tier-1-item-2 decision: either fix
   the defect and re-run, or explicitly document it as a known limitation of the historical model
   being reported.
4. **Decide Wu2021's fate.** Cannot submit a comparison table with numbers for a baseline that has
   zero implementation anywhere in the codebase. Either implement a minimal, faithful reproduction,
   or remove it from the comparison and disclose why.
5. **Rewrite the queue-loss claim** using the real (not forensic-approximation) numbers from item 1,
   reporting both `conditional_tx_failure_rate` and `fleet_tx_failure_rate` — the replacement
   language is already drafted in `MANUSCRIPT_IMPACT_MEMO.md` §2, pending real numbers.

### Tier 2 — strongly recommended before journal submission

1. **Add at least one non-trivial baseline** beyond AllOffload/NoOffload — a simple published
   heuristic (e.g., greedy proportional-fair RAT selection, or SINR-threshold-based offload
   decisions) is sufficient to change the comparison from "beats two trivial policies" to "beats a
   reasonable non-learned policy." This is the single highest-leverage addition for reviewer
   credibility.
2. **Statistical testing across seeds**, not just mean ± std. A paired test (or bootstrap CI) on
   the headline MA-ROPE-vs-AllOffload comparisons for each metric, given only 5 seeds are being
   run — reviewers will ask whether the differences reported are actually significant at that
   sample size.
3. **Test whether the WiFi6 over-reliance is trainable away.** The root-cause report explicitly
   flagged this as unresolved: is MA-ROPE's occasional use of the less-reliable RAT a converged
   policy choice, or an artifact of a not-fully-converged training run? A controlled experiment
   (more training episodes, or reward shaping that penalizes low-reliability RAT choices) directly
   answers this and is the actual evidence needed to decide between Path B and Path C (see §3).
4. **Sweep beyond the single `urllc` traffic scenario.** `SCENARIOS` defines `balanced` and
   `compute` mixes that were never exercised in the campaign — the Fleet OTR and queue-loss
   findings are currently only established for one task-mix regime; testing generality strengthens
   the claim considerably.

### Tier 3 — nice improvements

1. Extend the density sweep beyond N=32 if compute allows, to test whether the Fleet OTR
   advantage-widens-with-density trend continues or plateaus.
2. A dedicated privacy-utility tradeoff analysis for the Gaussian LDP component — it's present in
   the algorithm but not analyzed as its own experimental axis in anything reviewed here.
3. A formal (or at least empirical-convergence) analysis of FedAvg's behavior under the
   abort-below-70%-participation rule, since this directly affects how much agents actually
   synchronize during training — relevant context for the checkpoint-persistence finding.
4. Cross-validation against a second, independently-built simulator, or against the AG-executed
   run as an extra robustness data point beyond what's already been done for provenance purposes.

---

## 3. Path B vs. Path C — can the corrected implementation become either without changing the core research question?

**Core research question, as evidenced by the current codebase and experimental design**: does
federated multi-agent D3QN+PER, selecting among 4 heterogeneous RATs and continuous offload
ratios, outperform trivial offloading policies on a dual reliability/timeliness objective as fleet
density scales, under a differential-privacy constraint?

**Path B (Corrected MA-ROPE) — YES, without changing the research question.** Every fix made or
planned (metric rename, checkpoint persistence, energy formula, Wu2021 resolution) touches
*measurement and reporting*, not the algorithm, environment, or hyperparameters. The corrected
implementation is definitionally the same research question, answered more honestly. This is the
lower-risk, immediately-available path.

**Path C (MA-ROPE++) — NOT currently evidenced, and not recommended yet.** The root-cause
investigation's own verdict was explicit: "the algorithm itself is not shown to be broken." The one
concrete weakness found (WiFi6 over-reliance driving the per-attempt failure rate) has a plausible
explanation that doesn't require redesign — a not-fully-converged policy, or a reward function that
doesn't sufficiently penalize low-reliability RAT choices. Both are fixable *within* the existing
MA-ROPE framework (more training, reward shaping) — exactly the Tier 2, item 3 experiment above.
Moving to MA-ROPE++ before running that experiment would mean designing a new architecture to solve
a problem that hasn't been shown to require one, and would additionally violate the standing
instruction not to redesign the simulator or add new features at this stage.

**Recommendation: Path A of this question — pursue the Corrected MA-ROPE paper.** Revisit Path C
only if the Tier 2 convergence/reward-shaping experiment shows the RAT-selection sub-optimality
persists even under a fully-converged policy and well-shaped reward — that would be actual evidence
a structurally different design is needed, which does not exist today.
