# PHASE3C1_SANITY_COMPARISON.md

This document presents the outcomes of the controlled federated learning fixture and the environment smoke-training runs.

---

## 1. Controlled Federated Learning Fixture Results

* **Configuration:** 3 agents, 1-state MDP (optimal action $a=8$). Non-identical states representing distinct data distributions (Client 0: $S_0$, Client 1: $S_1$, Client 2: $S_2$).

### 1.1 Action Learning Outcome

| Mode | Client 0 Action | Client 1 Action | Client 2 Action | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Isolated** | 8 | 8 | 8 | **Learned** |
| **Centralized (Pooled)** | 8 | 8 | 8 | **Learned** |
| **Synchronous FedAvg** | 8 | 8 | 8 | **Learned** |

* **Analysis:** All three configurations successfully learned the optimal action $a=8$.

### 1.2 Model Parameter Divergence

At step 100, we computed the Frobenius norm distance (parameter divergence) between Client 0 and Client 1 online network weights:

* **Isolated Training Divergence:** **23.3003**
  * *Reasoning:* Because the agents train on completely non-overlapping state distributions ($S_0$ vs $S_1$), their network weights drift apart, resulting in a large divergence of 23.3003.
* **Synchronous FedAvg Divergence:** **0.0000**
  * *Reasoning:* Synchronous averaging every 10 steps overwrites local weights with the global average, forcing the model parameters to remain perfectly synchronized (divergence 0.0000).

---

## 2. Multi-RAT Environment Smoke-Training Results

* **Configuration:** 4 agents ($N=4$ vehicles), sync interval: 20, participation probability: 0.9. Mode: `physically_corrected`. Evaluated over 5 episodes.

### 2.1 Uniform vs PER Federated Progression

| Metric | Episode 1 | Episode 2 | Episode 3 | Episode 4 | Episode 5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Uniform Mean Reward** | 80.5255 | 76.8861 | 82.6678 | 84.4316 | 83.2420 |
| **PER Mean Reward** | 80.4094 | 80.9233 | 83.1891 | 83.3655 | 84.0142 |
| **Uniform Mean Loss** | 0.0962 | 0.0899 | 0.1332 | 0.2164 | 0.2950 |
| **PER Mean Loss** | 0.0706 | 0.0591 | 0.1116 | 0.1785 | 0.2579 |

### 2.2 Integrity Checks
1. **Numerical Stability:** Huber losses remain finite under both uniform and prioritized modes. No NaNs or infinite values occurred.
2. **Weight Updates:** We checked client state dicts before and after aggregation rounds (e.g. Round 1, 2) and verified parameters indeed changed coordinates upon synchronization.
3. **Data Privacy:** Replay buffers remained local; no client sampled from another client's experience buffer during training steps.
4. **Participation Drops:** Active agents properly dropped to 3 in some rounds, and rounds with $< 70\%$ (Round 9, 14 in both runs) successfully aborted weight aggregation.
