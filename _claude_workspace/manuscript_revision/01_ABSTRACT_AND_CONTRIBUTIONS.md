# Abstract and Contributions (Revision Draft v1)

Fresh draft, written directly from validated `CAMPAIGN_CORRECTED_20260803` data and
`LITERATURE_POSITIONING_REPORT.md`. No number here originates from the prior manuscript version.
This is working content for the revision — not yet placed into the LaTeX source of record.

---

## Abstract (draft)

Multi-RAT vehicular networks let vehicles choose among heterogeneous radio access technologies
(LTE, ITS-G5, 5G-NR, WiFi-6) for delay- and reliability-sensitive task offloading, but centralized
learning of this decision raises both a privacy problem (raw channel and task state reveals
vehicle behavior) and a scalability problem (a single controller cannot see every vehicle's local
state in real time). We present MA-ROPE, a federated multi-agent reinforcement learning system in
which each vehicle runs its own Dueling Double DQN agent with prioritized experience replay,
jointly selecting a radio access technology and a continuous, SINR-proportional offload ratio,
trained via periodic FedAvg aggregation under a local differential privacy budget. We evaluate
MA-ROPE against two honestly-reconstructed, disclosed non-learned baselines — a per-vehicle UCB1
contextual bandit over RAT/offload levels (UCB-RAT, in the spirit of a stateless multi-armed-bandit
RAT selector) and a task-property-only greedy offload rule (CoopEC-RAT) — plus the two trivial
extremes (always-offload, never-offload), across three fleet densities (N=8/16/32 vehicles) and
five random seeds each. MA-ROPE achieves the highest fleet-wide on-time-rate at every density
tested (0.888 at N=32, vs. 0.801 for the best non-learned baseline and 0.125 for always-offload),
with the advantage widening as fleet density increases. A fleet-scale reliability decomposition
further shows MA-ROPE reduces absolute transmission failures fleet-wide by roughly an order of
magnitude relative to always-offload, by learning to transmit selectively rather than reflexively —
a distinction between per-attempt and per-fleet reliability that, to our knowledge, is not reported
in comparable multi-RAT offloading literature. We validate the learned policy is a converged
characteristic rather than a training-duration artifact via an independent three-seed diagnostic
across a 5x range of training duration, and release a fully reproducible evaluation pipeline with
per-claim code/checkpoint provenance.

*(Word count target ~200-250 for TVT; this draft is ~220. Tone/claims are ready for review; wording
can tighten in a later pass.)*

---

## Contributions (draft, ready to become the Introduction's bulleted/enumerated list)

1. **A federated, privacy-preserving, jointly-learned RAT-and-offload-ratio policy.** Each vehicle
   runs an independent D3QN+PER agent over 11 discrete actions (RAT choice × discretized offload
   level), trained with FedAvg aggregation and a Gaussian local-differential-privacy mechanism on
   shared updates. The literature scan found federated RL for VEC offloading, multi-RAT DRL
   steering, and LDP-protected federated vehicular learning each active as separate lines of work
   in 2023-2026, but no single system combining per-vehicle multi-RAT selection with an adaptive
   offload ratio under LDP via federated D3QN+PER (`LITERATURE_POSITIONING_REPORT.md`).

2. **A fleet-wide reliability decomposition not found elsewhere in the surveyed literature.**
   We report both a conditional (per-transmission-attempt) and a fleet-wide (per-generated-task)
   failure rate, and show they can disagree in direction: MA-ROPE has a *higher* conditional
   failure rate than always-offload (5.46% vs. 2.46% at N=32) but a *lower* fleet-wide failure rate
   by roughly 10x (0.24% vs. 2.46%), because it transmits far less often and more selectively.
   Reporting either metric alone would materially mislead a reader about fleet-scale reliability.

3. **Two disclosed, non-learned baselines built specifically for honest comparison**, given that
   the original comparison targets could not be reproduced from any recoverable artifact
   (`BASELINE_TABLE_INTEGRITY_FINDING.md`). UCB-RAT (a per-vehicle UCB1 bandit) and CoopEC-RAT (a
   task-property-only greedy rule) are labeled throughout as reconstructions, not certified
   reproductions, and are independently validated end-to-end (from-scratch re-execution matching
   to 15 significant digits).

4. **A density-scaling result with a magnitude that is competitive against the closest comparable
   published DRL-vs-heuristic multi-RAT result found in the literature scan.** MA-ROPE's Fleet OTR
   advantage over CoopEC-RAT (the strongest baseline) is ~11% relative at N=32 and widens with
   density (MA-ROPE degrades 4.5 points from N=8→32 vs. CoopEC-RAT's 10-point drop); against
   UCB-RAT the advantage is a 2.6x ratio. The closest published comparison point (a 2024 hierarchical-
   RL multi-RAT traffic-steering paper) reports 8-13% throughput gains over DQN/heuristic baselines
   in a different but structurally analogous setting — evidence this magnitude of claim is
   defensible in the current literature, not inflated.

5. **A three-seed training-duration robustness check.** Training MA-ROPE to three checkpoints
   (100/250/500 episodes) across three independent seeds shows within-seed variation from 5x more
   training is the same size as or smaller than ordinary cross-seed noise, and inconsistent in
   direction — supporting that the learned RAT-usage pattern (including WiFi-6 reliance) is a
   converged policy characteristic, not an artifact of undertraining.

6. **A fully reproducible evaluation artifact.** Every reported number in this revision traces to a
   specific commit, config, seed set, and raw output path, independently re-verified (checkpoint
   hash recomputation, structural invariant checks, cross-campaign determinism checks, and one
   from-scratch independent re-execution) rather than taken on trust from any single run.

---

## What this draft deliberately does not claim

No comparison is made to the four other baselines named in earlier manuscript versions (MADDPG,
Lyapunov-Jing2019, GA+DQN-Yun2022) — they are omitted, not reproduced-and-shown-worse, because no
credible implementation target exists. This is stated plainly in the Related Work / Baselines
section (draft 03), not hidden. Energy is omitted from the results entirely for the same reason
(`ENERGY_METRIC_DECISION.md`) rather than reported with a known-invalid formula.
