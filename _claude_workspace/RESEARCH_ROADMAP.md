# RESEARCH_ROADMAP.md

Part 1 defines the scientific story for Path B (Corrected MA-ROPE), per `PUBLICATION_DECISION.md`'s
recommendation. This is a story design, not manuscript text — no prose from here should be copied
directly into the paper. Part 2 sequences the Tier 1/2/3 work from `PUBLICATION_DECISION.md` into
an actual plan with dependencies, so it's clear what blocks what.

---

## Part 1 — The scientific story

### Working title

*"MA-ROPE: Privacy-Preserving Federated Multi-Agent Reinforcement Learning for RAT-Aware Task
Offloading in Heterogeneous V2X Networks"*

Deliberately descriptive, not a rebrand — the algorithm and contribution haven't changed under
Path B, only the measurement and reporting have. A more evocative title tied to the
reliability/absolute-count tradeoff finding could work as a subtitle once Tier 1 numbers are final,
but shouldn't be locked in before that.

### Central hypothesis

Federated multi-agent D3QN with prioritized experience replay, jointly selecting radio access
technology and offload ratio under a differential-privacy constraint, reduces fleet-wide
transmission failures and improves task timeliness relative to static offloading policies as
vehicle density increases — even though, under a per-attempt failure-rate metric, its occasional
use of a less-reliable RAT can make it look worse than an always-transmit-on-the-most-reliable-RAT
baseline.

### Key contributions

1. A federated D3QN + PER architecture with an 11-action joint RAT/offload-ratio decision space
   across 4 heterogeneous RATs (LTE, ITS-G5, WiFi-6, 5G-NR), with Gaussian LDP applied to
   agent updates.
2. A dual utility formulation (U_PRR for reliability, U_OTR for timeliness) enabling a
   density-scaling analysis (N=8/16/32) rather than a single operating point.
3. A rigorously reproducible experimental pipeline — exact seeds, checkpoint hashing, campaign
   provenance manifests, independent hash-based validation rather than trusted self-reports. This
   is a legitimate secondary contribution: reproducibility failures are endemic in this subfield,
   and this pipeline is a concrete counterexample.
4. A precise, fully-decomposed account of why a single "queue loss" number can reverse depending on
   denominator choice (per-attempt vs. fleet-wide), with the mechanism traced to actual per-RAT
   physical-layer parameters rather than left as an unexplained anomaly. This is a methodological
   point with relevance beyond this one paper: a policy that transmits rarely but occasionally
   imperfectly can lose on a per-attempt metric while winning decisively on an absolute-count
   metric, and reporting only one of the two is misleading regardless of which one is chosen.

### Strongest evidence

- Fleet OTR's density-scaling direction (MA-ROPE's advantage over AllOffload widens as N grows)
  holds under two independent runs of the current codebase and is the one part of the original
  narrative that survives full scrutiny.
- The 11x absolute-failure-count advantage (35 vs. 385 failures out of the same 16,000
  vehicle-steps) is a real, decisive, well-evidenced result once the metric is decomposed correctly.
- The root-cause decomposition of the queue-loss reversal is complete and quantified — not "we
  think it's the denominator," but a full RAT-by-RAT, task-class-by-task-class breakdown pinning
  ~100% of the magnitude on two named, traceable mechanisms.
- The reproducibility infrastructure (B≈C agreement to 3-4 decimal places across independent runs
  months apart) is unusually strong for this subfield and directly supports every other claim's
  credibility.

### Weakest evidence

- **No non-trivial baseline.** Everything currently compares MA-ROPE against AllOffload/NoOffload
  only — this is the single biggest hole and the one most likely to draw an immediate desk concern
  from a reviewer.
- U_PRR, U_OTR, and Energy remain either uncorrected or undecided (Issue class 2, still open) —
  three of six headline metrics are not yet publication-ready numbers.
- Only 5 seeds — thin for any claim of statistical significance without an explicit test.
- Only one traffic-mix scenario (`urllc`) has been exercised; `balanced` and `compute` mixes exist
  in the codebase but haven't been run, so generalizability of the density-scaling finding is
  unverified outside the safety-heavy regime.
- Whether MA-ROPE's WiFi6 over-reliance is a converged policy choice or a training-convergence
  artifact is explicitly unresolved (flagged in the root-cause report, not yet tested).

### Reviewer risks

| Risk | Severity |
|---|---|
| "Your baselines are both trivial (always/never offload) — this doesn't establish competitiveness with any real alternative." | High — likely desk-level concern |
| "You redefined your headline metric during the review process — is this post-hoc metric selection to rescue an unfavorable result?" | High — a fair question given the paper's own history; must be answered with full transparency, not avoided |
| "Five seeds is not enough for the significance you're implying." | Medium |
| "You claim a privacy-preserving contribution (LDP) but never quantify the privacy-utility tradeoff." | Medium |
| "Your channel/RAT parameters (noise floors, path loss models) — how were these validated against real hardware or 3GPP measurements?" | Medium — standard simulation-paper scrutiny |
| "Results are only shown for one traffic-mix scenario; how general is the density-scaling claim?" | Medium |
| "Energy numbers look internally questionable (large swings, sign changes across variants)." | High if not fixed before submission |

### Expected reviewer questions and our responses

**Q: "You report two different failure-rate metrics for the same claim — isn't that cherry-picking
whichever one favors your method?"**
A: No — we report both, explain why they diverge (denominator choice), and are explicit that
MA-ROPE performs worse on the per-attempt metric. The paper's contribution here is *diagnosing* why
a single number is misleading, not selecting the favorable one. This is disclosed as a methodology
finding, not hidden in a footnote.

**Q: "Why no comparison against a published SOTA V2X offloading algorithm?"**
A: The originally planned comparator (Wu2021) has no recoverable, verifiable implementation; rather
than fabricate results against an unverified reimplementation, we [pending Tier 2 work] add a
transparent, simple heuristic baseline (e.g., SINR-threshold or proportional-fair RAT selection) as
a non-trivial reference point, and scope the SOTA comparison honestly as future work if a faithful
Wu2021 reproduction cannot be established.

**Q: "Is the WiFi6 over-reliance a fundamental limitation of your approach, or just undertraining?"**
A: [Pending the Tier 2 convergence experiment] — this is directly tested by extending training and
by reward shaping that penalizes low-reliability RAT choices; the result determines whether this is
reported as a known limitation or resolved before submission.

**Q: "How were the RAT physical-layer parameters chosen?"**
A: Per-RAT noise floor, path-loss model, and shadow-fading parameters are documented in
`env/config.py`'s `RAT_SPECS` and should be cited against their originating 3GPP/IEEE 802.11ax
standard references in the manuscript — a documentation task, not a re-derivation, but must be
explicit rather than left as unexplained constants.

**Q: "Does the density-scaling result hold outside a safety-critical traffic mix?"**
A: [Pending Tier 2 scenario sweep] — the `balanced` and `compute` scenarios in the existing
codebase directly test this; results pending.

---

## Part 2 — Sequenced roadmap

Referencing `PUBLICATION_DECISION.md`'s Tier 1/2/3 items by number; not repeating their content,
only their order and dependencies.

**Phase 1 — Unblock the data (Tier 1, strictly sequential, nothing else should start before this).**
Run the corrected campaign → validate against the 11-point checklist → make the Issue-class-2
re-baseline-vs-scope decision (this determines whether items 3-4 below are "fix code" or "document
as legacy model") → resolve the energy defect accordingly → resolve Wu2021's fate → rewrite the
queue-loss numbers with real (not forensic-approximation) data. Nothing in Phase 2 should begin
until the Issue-class-2 decision is made, since it changes the shape of several Tier 2 experiments
(e.g., whether a scenario sweep runs against re-baselined or legacy-scoped physics).

**Phase 2 — Strengthen the evidence (Tier 2, partially parallelizable).**
Highest priority within this phase: the convergence/reward-shaping experiment (Tier 2, item 3) —
this is the actual evidence gate for the Path B vs. Path C decision in `PUBLICATION_DECISION.md`
§3, so it should run early in Phase 2, not last. In parallel: add the non-trivial baseline (item 1)
and statistical significance testing (item 2) — both are independent of the convergence experiment
and don't block or get blocked by it. The scenario sweep (item 4) can run once Phase 1's physics
decision is settled, in parallel with the above.

**Phase 3 — Optional strengthening (Tier 3), only after a Phase 2 checkpoint.**
Not a prerequisite for submission. Take up only if Phase 1-2 results are strong enough that the
paper is otherwise submission-ready and additional runway exists before the deadline. Density
extension and the privacy-utility analysis are the two most likely to be worth the cost if pursued;
the FedAvg convergence-under-participation-threshold analysis and second-simulator cross-validation
are lower priority additions.

**Gate before writing begins in earnest**: do not invest significant manuscript-writing effort
until Phase 1 is complete and the Phase-2 convergence experiment has resolved the Path B vs. Path C
question — writing against numbers that Phase 1 will change, or against a research direction Phase
2 might redirect, is wasted effort.
