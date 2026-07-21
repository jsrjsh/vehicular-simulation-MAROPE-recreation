# ADR-001: Why D3QN?

## Context
In the MA-ROPE architecture, each vehicle acts as an independent agent deciding whether to execute tasks locally or offload them to an Edge server via LTE or 5G. This requires mapping a continuous observation space (task parameters, queue lengths, SINR) to a discrete action space.

## Decision
We selected the Dueling Double Deep Q-Network (D3QN) as the core reinforcement learning algorithm.

## Alternatives Considered
*   **Deep Q-Network (DQN)**: Prone to overestimating Q-values, leading to unstable policies in stochastic environments.
*   **Proximal Policy Optimization (PPO) / Soft Actor-Critic (SAC)**: These continuous-action algorithms are overly complex for our strict 11-dimensional discrete action space (1 Local, 5 LTE, 5 5G) and would require converting discrete decisions into continuous approximations.

## Consequences
*   **Positive**: The dueling architecture explicitly separates the value of the state (how congested the network is) from the advantage of each action, which is critical for load balancing. Double Q-learning prevents overestimation.
*   **Negative**: Requires significant hyperparameter tuning (target update frequency, replay capacity) and struggles to scale if the action space becomes continuous (e.g., fractional bandwidth allocation).
