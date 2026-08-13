# Method Section (Revision Draft v1)

Factual description of the implemented algorithm (`agents/d3qn/agent.py`,
`agents/federated/fedavg.py`, `agents/privacy/gaussian_ldp.py`). Hyperparameters quoted are read
directly from the code, not approximated.

### 5.1 Per-vehicle policy: Dueling Double DQN with prioritized experience replay

Each vehicle runs an independent agent over a 12-dimensional observation and the 11-action space
of Section 4.3. The Q-network is a dueling architecture (separate value and advantage streams);
targets are computed with Double-DQN action selection (online network picks the action, target
network evaluates it), trained with a weighted Huber loss over importance-sampling-weighted,
prioritized-replay-sampled transitions (priority exponent alpha=0.6, importance-sampling beta
annealed 0.4→1.0 over 50,000 steps). Exploration is epsilon-greedy with exponential decay
(epsilon 1.0→0.05, decay constant ≈668 steps); the target network is hard-updated every 100
learning steps; gradients are clipped to norm 10. Safety-class tasks have LTE actions
action-masked both at selection time and inside the Double-DQN target computation, so the learned
Q-values for those actions are never bootstrapped from safety-task transitions.

### 5.2 Federated aggregation

Per-vehicle online-network parameters are aggregated via sample-count-weighted FedAvg:
w_global = Σ_i (n_i / Σ_j n_j) · w_i, with strict validation before aggregation (rejects empty
client lists, parameter key/shape mismatches, and any NaN/Inf-valued client update) so a single
malformed client update cannot silently corrupt the global model. This validation is a real
implemented safeguard, not a paper-only claim — it is exercised by the existing test suite
(`tests/test_fedavg_coordinator.py`, `tests/test_fedavg.py`).

### 5.3 Local differential privacy on shared updates

Before aggregation, each client's model update is privatized via global-L2-norm clipping followed
by additive zero-mean Gaussian noise: Δ_clipped = Δ · min(1, C / (‖Δ‖₂ + η)), Δ_private =
Δ_clipped + N(0, σ²C²I), where C is the clip norm and σ the noise multiplier. The implementation
returns the achieved clipped/unclipped/noise norms and a resulting signal-to-noise ratio alongside
the privatized update, making the realized privacy-utility tradeoff directly measurable per
aggregation round rather than only nominally configured — this instrumentation itself is worth
reporting as a methodological point: privacy noise is not merely applied, its actual effect on the
update's SNR is logged every round.

### 5.4 Training procedure

Agents train against the environment of Section 4 for a fixed episode budget, with FedAvg
aggregation rounds occurring at a fixed cadence during training (round count and cadence are part
of the run's config/manifest, tied to the checkpoint's commit+seed+config record). All checkpoints
persist full per-agent online-network state dictionaries for every vehicle in the fleet (not only
a subset), enabling exact resume and, separately, exact independent re-verification of any reported
checkpoint by hash.

### 5.5 What is new relative to the base architecture, stated plainly

D3QN and PER are each individually established, current techniques (Section 6.4's Related Work
citation to 2024/2025 work confirms this). The contribution here is not a new base learner; it is
the specific combination applied to this problem — federated training across vehicles, a joint
RAT-and-continuous-offload-ratio action space, and an LDP mechanism with measured per-round
privacy-utility tradeoff — which Section 6.5 argues is not found combined elsewhere in the
surveyed literature.
