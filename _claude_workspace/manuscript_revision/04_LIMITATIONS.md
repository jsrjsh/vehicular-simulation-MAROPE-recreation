# Limitations Section (Revision Draft v1)

Four items, ordered by how likely each is to be raised by a TVT reviewer. Grounded in code and
existing decision records (`docs/adr/ADR-004-Why-Shannon-Capacity.md`,
`docs/adr/ADR-005-Why-Synthetic-Mobility.md`), not new speculation — these ADRs were written
earlier in this project and already anticipated the two most significant items below.

### 7.1 Mobility and channel-layer abstraction (the most reviewer-visible item)

This evaluation uses a synthetic, stochastic mobility model — vehicle coordinates are re-sampled
at each simulation step rather than following continuous, physically-consistent trajectories — and
a deterministic distance-based path-loss model combined with the Shannon-Hartley bound, rather
than a full network simulator. Concretely: no SUMO-generated traffic trajectories (car-following,
intersection topology, realistic spatial clustering) and no ns-3-level MAC-layer contention, true
packet-level drops, or handover modeling. `ADR-005` and `ADR-004` document this as a deliberate,
explicit choice made to isolate the RL and FedAvg dynamics under a fast, deterministic, tractable
environment (full training campaigns complete in hours, not days), at the cost of not capturing
real-world congestion and mobility correlation effects — both ADRs already flag SUMO/ns-3
integration as "the Next Research Phase," not an oversight discovered now.

**Framing for the paper**: this should be stated as a first-class limitation in the paper's own
words, not left for a reviewer to discover. The claims in this paper are about the learned
decision policy's behavior (RAT/offload-ratio selection under a stylized but physically-grounded
SINR/Shannon model) and about the federated/privacy mechanism — not about absolute real-world
throughput or delay numbers, which would require the higher-fidelity simulator. This distinction
should appear explicitly in both the Introduction (scoping the claim) and here.

### 7.2 Scale tested (N=32 ceiling)

All results are reported at fleet densities up to 32 vehicles. The Fleet OTR advantage widens with
density in the tested range, which is a real, validated trend (Section 5.3), but extrapolating
that trend to city-scale fleets (hundreds of vehicles per RSU) is not validated here and should not
be implied. This matters specifically because government/deployment conversations (Section on
future work) will ask about exactly this scale.

### 7.3 Only two non-learned baselines, both disclosed reconstructions

UCB-RAT and CoopEC-RAT are honest, non-certified reconstructions built because the paper's
originally-intended comparators (MADDPG, a Lyapunov-optimization policy, a GA+DQN policy) had no
independently-executable implementation recoverable with confidence. This is disclosed in Results
5.5, not hidden — but it does mean this paper does not claim superiority over the *specific*
published algorithms those names refer to, only over the general policy classes they represent
(a stateless bandit and a non-adaptive greedy rule).

### 7.4 Statistical power (5 seeds, no formal significance testing)

All comparisons use mean ± population standard deviation across 5 seeds per cell. This is enough
to see that MA-ROPE's Fleet OTR advantage (e.g., 0.888 ± 0.014 vs. CoopEC-RAT's 0.801 ± 0.004) is
well outside 1-2 standard deviations of overlap, but no formal paired significance test (e.g., a
paired t-test across matched seeds, with multiple-comparison correction across the metric table)
has been run. This is a cheap, mechanical addition worth doing before final submission — it does
not require new experiments, only a statistics pass over existing per-seed CSV rows.

### 7.5 Not covered in this revision, flagged for completeness

Federated-learning robustness to adversarial or straggler clients (Byzantine agents, poisoning of
shared updates) is not evaluated — FedAvg here assumes all clients are honest. On-vehicle
real-time inference feasibility (whether the trained D3QN network meets embedded-hardware latency
budgets) is not measured; only simulated decision quality is. Both are reasonable "future work"
items for a follow-on paper, not gaps that undermine this paper's actual claims, which are scoped
to decision-quality and reliability under the stated simulation model.
