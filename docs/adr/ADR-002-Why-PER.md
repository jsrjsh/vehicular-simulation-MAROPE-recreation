# ADR-002: Why Prioritized Experience Replay (PER)?

## Context
In highly dynamic vehicular environments, most state transitions are mundane (e.g., successful offload with standard latency), while a small subset of transitions are highly instructive (e.g., SLA violations due to sudden queue spikes or SINR drops).

## Decision
We utilize Prioritized Experience Replay (PER) rather than uniform random sampling for the replay buffer.

## Alternatives Considered
*   **Uniform Experience Replay**: Samples transitions randomly. Computationally cheaper but highly inefficient in learning from rare, high-error boundary cases.

## Consequences
*   **Positive**: Dramatically accelerates convergence by forcing the agent to learn from its biggest mistakes (highest TD error).
*   **Negative**: Adds computational overhead during the sampling and weight-updating phases. Introduces hyperparameter complexity ($\alpha$, $\beta$) to correct for sampling bias.
