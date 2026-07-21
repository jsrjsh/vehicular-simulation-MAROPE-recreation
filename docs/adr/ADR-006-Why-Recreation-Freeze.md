# ADR-006: Why Recreation++ Freeze?

## Context
Reinforcement Learning projects are notoriously prone to "feature creep." As experiments reveal sub-optimal convergence (e.g., the FedAvg 200-episode Always-5G collapse), the instinct is to immediately tweak the reward function, algorithm, or environment.

## Decision
We enacted a strict code freeze on the "Recreation++" baseline architecture before executing long-horizon benchmarks or introducing Local Differential Privacy (LDP).

## Alternatives Considered
*   **Iterative Tuning**: Continuously tweaking the reward weights or MEC capacity until the graphs "look good."

## Consequences
*   **Positive**: Forces us to treat the environment as a scientific constant. By freezing the architecture and running a 1000-episode benchmark, we isolate whether observed behavior is a fundamental optimization failure or simply an artifact of an insufficient training horizon. Ensures absolute reproducibility for future researchers.
*   **Negative**: Delays the implementation of novel algorithmic improvements and forces us to document and justify the failure modes of the baseline.
*   **Resolution**: Cultivates extreme engineering discipline. Novelty will only be introduced once the frozen baseline is fully understood.
