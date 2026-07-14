# PHASE3B2_SANITY_COMPARISON.md

This document compares the learning performance and numerical stability of **Uniform Experience Replay** and **Prioritized Experience Replay (PER)** in the single-agent Dueling Double DQN configuration.

---

## 1. 1-State Deterministic Learning Fixture Comparison

Both modes were evaluated on the 1-state MDP across the same 5 seeds (0, 1, 2, 3, 4). The table below lists the number of updates (learning steps) required before the agent's greedy policy successfully chose the optimal action ($a=8$).

| Seed | Uniform Replay Steps | Prioritized Replay Steps | Variance Analysis |
| :--- | :---: | :---: | :--- |
| **Seed 0** | 1 step | 2 steps | Both converged immediately. |
| **Seed 1** | 4 steps | 0 steps | PER learned instantly (0 steps after buffer fill). |
| **Seed 2** | 1 step | 0 steps | PER learned instantly. |
| **Seed 3** | 1 step | 3 steps | Both converged immediately. |
| **Seed 4** | 3 steps | 1 step | PER learned faster. |
| **Average** | **2.0 steps** | **1.2 steps** | PER reduces the steps to reach the optimal choice. |

* **Convergence Instability:** None observed. Both methods converged stably to the optimal action $a=8$ on every seed.
* **Q-value Ranking:** At step 150, the Q-value of action 8 was ranked #1 across all seeds and modes.

---

## 2. Multi-RAT Environment Smoke-Training Comparison

Both modes were evaluated in `V2XEnv` under `physically_corrected` mode across 5 episodes (100 steps/episode) using seed 42.

### 2.1 Metric Progression Comparison

| Metric | Episode 1 | Episode 2 | Episode 3 | Episode 4 | Episode 5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Uniform Reward** | 79.0459 | 88.1328 | 75.5682 | 78.5454 | 85.6380 |
| **PER Reward** | 79.0021 | 88.4513 | 77.5046 | 81.2738 | 85.8789 |
| **Uniform Loss** | 0.0577 | 0.0471 | 0.0709 | 0.0861 | 0.0942 |
| **PER Loss** | 0.0326 | 0.0260 | 0.0488 | 0.0639 | 0.0875 |
| **Epsilon ($\epsilon$)** | 0.9018 | 0.7763 | 0.6683 | 0.5754 | 0.4953 |

### 2.2 Numerical & Qualitative Differences
1. **Huber Loss Trajectory:** PER exhibits a slightly lower mean Huber loss. This is expected because PER scales losses by importance sampling weights ($w'_i \le 1.0$), which dynamically bounds and scales back large losses to prevent gradient spikes.
2. **Action Diversity:** Both agents exhibit good action exploration early in training ($\epsilon > 0.5$). There was no premature action collapse or locking on a singleRAT.
3. **TD-Error and Priorities:**
  * **Uniform:** TD errors are computed but ignored for sampling. Priorities are flat.
  * **PER:** Absolute TD-errors are successfully tracked and saved. High TD-error transitions are correctly resampled, allowing the agent to focus updates on transitions with larger learning gaps.
