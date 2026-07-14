# PHASE3C2_SANITY_COMPARISON.md

This document presents a comparative analysis of the training runs under varying Local Differential Privacy (LDP) levels, demonstrating the utility-privacy trade-offs.

---

## 1. 3-Agent Learning Fixture Comparison

The table below lists the success rate (number of seeds out of 5 that converged to the optimal action $a=8$ on the 1-state MDP) under different update perturbation standard deviations ($\sigma$):

| Privacy Level | Noise Multiplier ($\sigma$) | Clipping Norm ($C$) | Convergence Success Rate (out of 5) | Analysis & Observations |
| :--- | :---: | :---: | :---: | :--- |
| **No Privacy** | 0.0 | 5.0 | **5 / 5** | Converges stably across all seeds. |
| **Weak Privacy** | 0.1 | 5.0 | **0 / 5** | Small parameter fluctuations displace Q-value ranking. |
| **Moderate Privacy** | 0.5 | 5.0 | **0 / 5** | Weight coordinates drift, disrupting greedy policy choice. |
| **Strong Privacy** | 2.0 | 5.0 | **0 / 5** | Large noise variance dominates weight changes. |

* **Privacy-Utility Trade-off:** The 1-state MDP training is extremely short (100 steps, with aggregation every 10 steps). Under short learning steps, adding Gaussian perturbation to parameter updates limits convergence stability.

---

## 2. Multi-RAT Environment Smoke-Training Comparison

We evaluated the federated system in `V2XEnv` under four privacy budget levels. Below is the comparative log of rewards and Huber loss values over a 2-episode run:

| Privacy Mode | Episode 1 Reward | Episode 2 Reward | Episode 1 Mean Loss | Episode 2 Mean Loss | Derived Noise ($\sigma$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **None** | 80.5255 | 76.8861 | 0.0962 | 0.0899 | 0.0000 |
| **LDP ($\epsilon = 10.0$)** | 80.0513 | 79.9834 | 50,307.09 | 195,900.08 | 0.4845 |
| **LDP ($\epsilon = 2.0$)** | 80.0020 | 78.9474 | 5.11e+07 | 2.10e+08 | 2.4224 |
| **LDP ($\epsilon = 0.5$)** | 80.0020 | 78.9474 | 1.44e+10 | 5.87e+10 | 9.6896 |

---

## 3. Key Observations & Invariants

### 3.1 Loss Scaling under Gaussian Noise
* The local agent Huber loss evaluates target network mismatches. Adding Gaussian noise to weights causes the online network parameter values to fluctuate, creating a large discrepancy between the online network's Q-values and the target network's Q-values.
* As a result, the Huber loss values grow exponentially with larger noise levels (smaller epsilon).

### 3.2 Signal-to-Noise Ratio (SNR)
* **High Epsilon ($\epsilon = 10.0$):** Yields lower noise standard deviation ($\sigma = 0.4845$), resulting in higher Signal-to-Noise Ratio (SNR) and preserving global model structure.
* **Low Epsilon ($\epsilon = 0.5$):** Yields larger noise standard deviation ($\sigma = 9.6896$), resulting in lower SNR, where noise dominates client weight updates.

### 3.3 Integrity Check Validation
* **Finite parameters:** Online networks do not contain any NaN or Infinite values post-aggregation.
* **Repeatability:** Evaluation remains completely deterministic under a fixed privacy seed.
* **No network overhead change:** The communication bytes transferred per round remains exactly **4298.49 KB** (constant model size), showing that privacy noise does not alter communication footprint.
