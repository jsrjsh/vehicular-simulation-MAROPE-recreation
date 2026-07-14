# LDP_AMBIGUITIES.md

This document lists all ambiguities identified during the implementation of Local Differential Privacy (LDP) and documents our technical resolutions.

---

## Identified Ambiguities

### Ambiguity 1: Layer-by-Layer vs. Global Clipping
* **Description:** It is not specified whether the clipping norm $C$ should be applied layer-by-layer to each weight matrix individually, or globally across the flattened parameter update vector.
* **Resolution:** We implemented **global clipping** across the entire update tensor set:
  $$\|\Delta_i\|_2 = \sqrt{\sum_j \|\Delta_{i,j}\|_2^2}$$
* **Rationale:** Layer-by-layer clipping changes the relative direction of the model update vector across different layers, which introduces optimization bias. Global clipping preserves the update vector's direction, scaling only its magnitude, which stabilizes training convergence.

### Ambiguity 2: Epsilon/Delta to Noise Multiplier ($\sigma$) Mapping
* **Description:** The guide mentions using privacy parameters $\epsilon, \delta$ but does not specify the exact conversion formula to compute the standard deviation multiplier $\sigma$.
* **Resolution:** We adopted the classical Gaussian mechanism conversion formula:
  $$\sigma = \frac{\sqrt{2 \ln(1.25 / \delta)}}{\epsilon}$$
* **Rationale:** This is the standard analytical approximation for $(\epsilon, \delta)$-DP under the Gaussian mechanism. We explicitly document this mapping and support both direct $\sigma$ inputs and $(\epsilon, \delta)$ parameter inputs.

### Ambiguity 3: Independent Seeding per Client and Round
* **Description:** The guide requires deterministic seeds for privacy noise, but does not define how to prevent noise correlation across different clients or rounds under a fixed seed.
* **Resolution:** We seed the random number generator for each client and round independently using:
  $$\text{round\_seed} = \text{base\_seed} + \text{client\_idx} + \text{round\_idx} \cdot 1000$$
* **Rationale:** A static seed across all clients would lead to identical noise vectors being added to different updates, which allows the server to cancel out the noise by averaging them (collusion/average noise cancellation). Varying the seed by client and round indices guarantees statistical independence of perturbation vectors.

### Ambiguity 4: No Target Network Perturbation
* **Description:** It is not specified if target network weights should receive separate privacy noise.
* **Resolution:** Target network parameters are **never noised**. Post-broadcast, clients overwrite their target networks with a clean copy of the aggregated global online model.
* **Rationale:** Target network parameter averaging is out-of-scope and would introduce double-noising, causing training to fail. Target networks must follow the online weights directly.
