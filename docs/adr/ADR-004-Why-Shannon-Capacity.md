# ADR-004: Why Shannon Capacity instead of ns-3?

## Context
The simulation requires calculating the time taken to transmit a task from a vehicle to an Edge server over LTE or 5G. This requires a model of the physical wireless layer.

## Decision
We used a deterministic distance-based path-loss model mapped to the Shannon-Hartley theorem to approximate channel capacity, rather than using a full network simulator like ns-3.

## Alternatives Considered
*   **ns-3 Co-simulation**: The gold standard for network simulation, handling MAC-layer contention, true packet drops, fading, and handovers.

## Consequences
*   **Positive**: Maximizes execution speed, allowing for 1000-episode RL training horizons in under 2 hours. Ensures mathematical tractability and perfect determinism for analyzing RL algorithm behavior.
*   **Negative**: Fails to capture the complex real-world dynamics of network congestion, MAC-layer collisions, or spatial fading.
*   **Resolution**: This is a deliberate abstraction for the Recreation++ phase. Full ns-3 integration is explicitly scheduled for the Next Research Phase.
