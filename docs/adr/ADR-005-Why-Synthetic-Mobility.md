# ADR-005: Why Synthetic Mobility?

## Context
Vehicular Edge Computing depends heavily on vehicle locations, which dictate distance to the RSU, line-of-sight probabilities, and ultimately the SINR.

## Decision
We implemented a synthetic, stochastic mobility model where vehicles are assigned random coordinates within the simulation area at each time step.

## Alternatives Considered
*   **SUMO Co-simulation**: The gold standard for vehicular traffic, providing realistic car-following mechanics, intersection topologies, and continuous trajectories.

## Consequences
*   **Positive**: Dramatically reduces the computational overhead of the environment step function. Simplifies the state space by removing temporal position correlation.
*   **Negative**: Prevents the use of recurrent neural networks (RNNs/LSTMs) for trajectory prediction, as the vehicle locations lack temporal continuity. Eliminates realistic spatial clustering (e.g., traffic jams).
*   **Resolution**: Deliberately abstracted for Recreation++ to isolate the core RL and FedAvg dynamics. SUMO integration is scheduled for the Next Research Phase.
