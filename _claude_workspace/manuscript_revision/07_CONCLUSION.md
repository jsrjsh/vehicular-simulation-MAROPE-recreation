# Conclusion Section (Revision Draft v1)

We presented MA-ROPE, a federated multi-agent reinforcement learning system in which vehicles
jointly learn a radio-access-technology selection and a continuous offload ratio under a local
differential privacy budget, and evaluated it against two disclosed, honestly-reconstructed
non-learned baselines across three fleet densities and five seeds. MA-ROPE achieves the best
fleet-wide on-time rate at every density tested, with the advantage widening as density increases,
and reduces absolute fleet-wide transmission failures by roughly an order of magnitude relative to
naive full offloading — a fleet-scale reliability effect that a per-attempt failure-rate metric
alone would miss. A three-seed training-duration diagnostic supports that the learned policy's
RAT-usage pattern is a converged characteristic rather than a training artifact. The specific
combination evaluated here — per-vehicle multi-RAT selection, a continuous offload ratio, federated
training, and a measured local-differential-privacy mechanism — does not appear, in a targeted
literature scan, to have been previously combined and evaluated together.

This work is explicitly scoped: results are reported under a fast, analytically-tractable
mobility/channel model rather than a SUMO/ns-3 co-simulation (Section 7.1), at fleet densities up
to 32 vehicles (Section 7.2), and against two policy-class baselines rather than certified
reproductions of specific named algorithms (Section 7.3). Within that stated scope, the reliability
and density-scaling results are real, validated, and reproducible end-to-end from released code,
seeds, and checkpoints.

**Future work**, in order of what would most directly extend this paper's claims: (1) SUMO/ns-3
co-simulation to validate the learned policy's behavior under realistic mobility and MAC-layer
contention — already anticipated in this project's own design records as the next phase; (2) fleet
densities beyond 32 vehicles to test whether the observed density-scaling advantage continues to
widen or saturates; (3) a from-specification reproduction of at least one certified published
baseline, if an implementable specification becomes available; (4) robustness evaluation of the
federated aggregation under adversarial or straggler clients; (5) on-vehicle inference-latency
measurement against real embedded hardware budgets.
