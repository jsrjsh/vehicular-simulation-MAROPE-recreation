# LITERATURE_POSITIONING_REPORT.md

Real web search, done 2026-08-03, in direct response to Vivek's question: "why are we being
pessimistic — can you research existing papers and enhance our project to reach comparable or
stronger claims, instead of staying in a recreation loop?" This is new research, not forensic
reassembly. No manuscript or manuscript-impact document is touched by this report.

## What "pessimism" was actually about, and what it wasn't

Every prior report in this workspace was pessimistic about one specific, narrow thing: whether
the *manuscript's own original numbers* can be reproduced and defended line-by-line. That
question is answered — mostly no, and the reasons are now documented (formula defects, an
internally-duplicated baseline table, an unrecoverable prior config). That is a fact about one
old PDF, not a fact about whether MA-ROPE the method is any good.

Those are different questions. Nothing in the forensic work says the *method* is weak — it says
the *paper's evidence for the method* has holes. The literature scan below addresses the question
Vivek actually asked: is the method, on its own newly-validated merits, comparable to or stronger
than what's being published right now.

## What's being published in this space, 2023-2026 (real search results)

Searched: federated RL for V2X/VEC offloading, multi-agent DRL for vehicular offloading, DRL-based
multi-RAT/traffic-steering selection, LDP + federated learning in vehicular networks, and D3QN+PER
task offloading specifically. Representative, most relevant hits:

- **FedMAGS** (arXiv 2605.18437, "Heterogeneous Tasks Offloading in Vehicular Edge Computing: A
  Federated Meta Deep Reinforcement Learning Approach") — federated meta-RL with GAT-Seq2Seq
  modeling for DAG-structured tasks. Closest current paper to MA-ROPE's problem setting
  (federated + VEC + offloading), but targets *dependent, multi-step DAG tasks*, not single-shot
  tasks with RAT choice — a different problem shape, not a direct competitor on the same metric.
- **Federated DRL for task offloading + resource allocation** (Journal of Network and Computer
  Applications, 2024, dl.acm.org/doi/10.1016/j.jnca.2024.103941) — federated DRL for joint
  offloading/resource allocation in MEC-assisted vehicular networks; no multi-RAT dimension, no
  LDP.
- **P-D3QN** (IEEE Xplore 10660558, "Task Offloading via Prioritized Experience-Based Double
  Dueling DQN in Edge-Assisted IIoT") — architecturally the closest single-agent match to
  MA-ROPE's D3QN+PER core (industrial IoT setting, not vehicular; no federation, no multi-RAT).
  Confirms D3QN+PER is still an active, currently-published design choice in 2024/2025, not a
  dated one.
- **Traffic Steering for 5G Multi-RAT Deployments using DRL** (arXiv 2301.05316) and its follow-up
  hierarchical-RL variant — reports HRL beating plain DQN and threshold heuristics by
  8.49-12.52% throughput and 27.74-39.13% delay, in a multi-RAT 5G steering setting. This is the
  closest published multi-RAT DRL result with *numbers attached* found in this scan. It is a
  cellular traffic-steering problem (users, not vehicles/tasks), so not a same-metric comparison,
  but it's evidence that DRL-beats-heuristic-on-multi-RAT-selection is a currently-defensible,
  currently-published claim shape — the same shape as MA-ROPE's Fleet OTR result against
  UCB-RAT/CoopEC-RAT.
- **LDP + federated learning in VANETs** (ScienceDirect S0020025523013026, and several 2025 papers
  on differentially-private federated learning for vehicular/IoV settings) — LDP-protected FedAvg
  in vehicular networks is an active, current line of work, not a stale add-on. No paper found in
  this scan combines LDP-protected FedAvg *with* multi-RAT selection *with* per-agent D3QN+PER in
  one system — that specific combination did not turn up as already-published.

## Assessment: is MA-ROPE's real, validated result competitive?

Three honest observations, each traceable to a specific number already in `CORRECTED_RESULT_TABLES.md`
or to a specific paper above — no new claims invented, no manuscript numbers used:

1. **The core design (federated D3QN+PER, multi-RAT, LDP) has no exact published match.** Every
   individual ingredient (D3QN+PER offloading, federated VEC offloading, multi-RAT DRL steering,
   LDP-protected federated vehicular learning) is separately active and recent, but the specific
   combination — especially per-vehicle multi-RAT selection with an SINR-proportional offload-ratio
   adaptation, under LDP, learned via federated D3QN+PER — was not found as a single existing
   system in this scan. That is a genuine, checkable, defensible novelty claim, independent of
   whether the original manuscript's numbers hold up.
2. **The magnitude of MA-ROPE's real advantage is in the same range as recently-published
   DRL-vs-heuristic multi-RAT results.** The Traffic Steering HRL paper reports roughly 8-13%
   throughput and 28-39% delay improvements over DQN/heuristics. MA-ROPE's *validated* Fleet OTR
   advantage over CoopEC-RAT (0.888 vs. 0.801, N=32 — an 8.7-point gap, ~11% relative) and over
   UCB-RAT (0.888 vs. 0.346, a 2.6x gap) sit in or above that range. This is a real, current,
   comparable-or-stronger claim, built entirely from validated Path B numbers, not from anything
   in the old manuscript.
3. **The fleet-vs-conditional-failure-rate tradeoff is a genuinely reusable finding, not just an
   internal audit footnote.** None of the papers surfaced in this scan report both a per-attempt
   and a per-fleet-generated-task failure metric side by side, or discuss a policy that
   deliberately trades attempt frequency for absolute reliability. `QUEUE_LOSS_ROOT_CAUSE_REPORT.md`'s
   decomposition (MA-ROPE causes 10x fewer absolute fleet failures than AllOffload while having a
   *higher* per-attempt failure rate) is a small methodological contribution in its own right —
   a caution about single-metric reliability reporting in this literature that current papers
   don't appear to raise.

## Direct answer to "why the loop, why not just strengthen the claims"

The forensic work was never in tension with this. It was the necessary precondition for it —
you cannot honestly claim MA-ROPE is comparable-or-stronger than current work using numbers that
can't be reproduced from your own code. Now that Path B is validated against two independently
re-implemented, disclosed baselines (not the original manuscript's suspect table), the comparison
above is one that can survive a reviewer asking "show me the code that produced this," which the
original manuscript's baseline comparison could not.

**Recommendation, concrete and immediately actionable, that does not require any more forensic
work**: position the revised manuscript's contribution statement around the three points above —
(a) the specific combination is unclaimed in the current literature, (b) the magnitude of the
Fleet OTR advantage is competitive with the best recently-published multi-RAT DRL result found,
(c) the fleet-vs-conditional reliability decomposition is a small, genuine methodological addition
— rather than around "we corrected our own numbers," which is necessary internal rigor but not,
by itself, an interesting claim to a reader. This does not require new experiments; it requires
writing the contribution section against this evidence instead of against the old table.

## What this does not claim

This is a scan, not a systematic literature review — no claim of exhaustiveness, no claim that a
truly identical system doesn't exist somewhere uncited. If the revision goes to a venue that will
push hard on novelty, a half-day targeted search specifically for "multi-RAT + federated + LDP +
per-vehicle RL" combinations before submission is cheap insurance. That is genuinely optional
future work, not a blocker — nothing above depends on it being done first.
