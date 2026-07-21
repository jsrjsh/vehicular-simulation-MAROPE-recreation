# ADR-003: Why Federated Averaging (FedAvg)?

## Context
With multiple vehicular agents learning simultaneously, sharing knowledge can accelerate convergence. However, transmitting raw replay buffers (centralized RL) violates privacy constraints and consumes excessive uplink bandwidth.

## Decision
We implemented Synchronous Federated Averaging (FedAvg) as the aggregation strategy.

## Alternatives Considered
*   **Centralized RL**: Too much bandwidth overhead. Violates privacy.
*   **Asynchronous Federated Learning**: Harder to analyze mathematically and reproduce. Could lead to stale gradients corrupting the global model.

## Consequences
*   **Positive**: Strictly preserves privacy by only transmitting model weights. Greatly reduces communication overhead. Establishes a rigid mathematical baseline for future Local Differential Privacy (LDP) noise injection.
*   **Negative**: Synchronous aggregation is vulnerable to stragglers. We mitigated this by enforcing a strict latency deadline for aggregation eligibility.
