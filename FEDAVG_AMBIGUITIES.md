# FEDAVG_AMBIGUITIES.md

This document lists all ambiguities identified during the implementation of Synchronous Federated Averaging (FedAvg) and documents our technical resolutions.

---

## Identified Ambiguities

### Ambiguity 1: Decoupling of Exploration ($\epsilon$) Schedules
* **Description:** The guide does not state whether vehicles should share a global epsilon exploration state or decay their epsilons locally.
* **Resolution:** Epsilon parameters decay strictly **locally** based on each vehicle's local environment steps.
* **Rationale:** Localizing exploration allows different vehicles to explore/exploit asynchronously based on their local state encounters, which prevents globally synchronized explore/exploit phases and yields more stable training distributions.

### Ambiguity 2: FedAvg weight calculation under PER
* **Description:** When using Prioritized Experience Replay, client updates could theoretically be weighted by the sum of priorities of the sampled transitions rather than flat sample counts.
* **Resolution:** Client update weights scale strictly with the **count of local training steps ($n_i$)** completed during the synchronization epoch.
* **Rationale:** This preserves standard FedAvg semantics ($w_{\text{global}} = \sum \frac{n_i}{N} w_i$) and prevents highly prioritized local samples from disproportionately steering the global updates.

### Ambiguity 3: Local Optimizer State Resetting
* **Description:** When client models are overwritten with the aggregated global model, it is not specified whether their optimizer momentum/states should be reset or preserved.
* **Resolution:** We **reinitialize (reset) the client's Adam optimizer** upon global parameter broadcast.
* **Rationale:** Keeping old momentum vectors from old local weights can cause gradient drift and instability when applied to the new global parameter coordinates.

### Ambiguity 4: Target Network Sync Post-Broadcast
* **Description:** The target update frequency is "every 100 steps". It is not clear whether this refers to local learning steps or is synchronized globally.
* **Resolution:** Post-broadcast, each client hard-copies the new global online weights to its local target network.
* **Rationale:** This ensures that target networks are synchronized with the global weights, preventing target values from being computed using outdated local networks.
