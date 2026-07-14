# PHASE3B1_TRAINING_SANITY_REPORT.md

This document reports the sanity verification of the Dueling Double DQN training runs, detailing the outcomes of the tiny learning fixture and the environment smoke-training.

---

## 1. Tiny Deterministic Learning Fixture Results

* **Description:** 1-state MDP where selecting action 8 yields $r = 1.0$, and other actions yield $r = 0.0$.
* **Seeds evaluated:** 0, 1, 2, 3, 4.
* **Steps per seed:** 150.
* **Evaluation Criteria:** Epsilon set to 0.0 (pure exploitation). Greedy action selection must be exactly index 8.

### Execution Results
* **Seed 0:** Greedy action = **8** (SUCCESS)
* **Seed 1:** Greedy action = **8** (SUCCESS)
* **Seed 2:** Greedy action = **8** (SUCCESS)
* **Seed 3:** Greedy action = **8** (SUCCESS)
* **Seed 4:** Greedy action = **8** (SUCCESS)

* **Analysis:** The D3QN agent reliably converges to the optimal action ($a=8$) across all 5 seeds. This verifies that:
  1. The experience replay buffer correctly inserts and samples transitions.
  2. Dueling heads recombine Advantage and Value gradients correctly.
  3. The Adam optimizer propagates weights in the correct direction.
  4. Argmax-based greedy selection extracts the correct preferred Q-value index.

---

## 2. Multi-RAT Environment Smoke-Training Results

* **Configuration:** Single agent ($N=1$ vehicle), Scenario: URLLC Stress (`urllc`), Mode: Physically Corrected (`physically_corrected`), Episodes: 5, Steps per episode: 100.
* **Replay:** Uniform sampling (no PER).
* **Aggregation:** None (no FedAvg).

### Training Log
* **Episode 01:** Total Reward = **79.1179** | Mean Huber Loss = **0.0511** | Epsilon = **0.9018**
* **Episode 02:** Total Reward = **88.1836** | Mean Huber Loss = **0.0463** | Epsilon = **0.7763**
* **Episode 03:** Total Reward = **76.8120** | Mean Huber Loss = **0.0662** | Epsilon = **0.6683**
* **Episode 04:** Total Reward = **80.7571** | Mean Huber Loss = **0.0800** | Epsilon = **0.5754**
* **Episode 05:** Total Reward = **85.3508** | Mean Huber Loss = **0.0872** | Epsilon = **0.4953**

* **Evaluation (after 5 smoke episodes, $\epsilon=0.05$):**
  * **Episode 1:** Reward = **92.4231** | Mean Latency = **79.45** ms | Mean Energy = **0.1598** J | Sidelink success = **100.0%**
  * **Episode 2:** Reward = **91.1248** | Mean Latency = **87.02** ms | Mean Energy = **0.1750** J | Sidelink success = **97.0%**
  * **Episode 3:** Reward = **89.7916** | Mean Latency = **92.33** ms | Mean Energy = **0.1857** J | Sidelink success = **97.0%**
  * **Averages:** Reward: **91.1132** | Latency: **86.27** ms | Energy: **0.1735** J | Success: **98.0%**

### Analysis of Smoke Training
1. **Numerical Stability:** The Huber loss remains finite, and rewards/observations do not contain any NaN or Infinite values.
2. **Epsilon Greedy Decay:** Epsilon decays exponentially according to schedule, scaling from $1.0$ down to $0.4953$ over the 500 environment transitions.
3. **Checkpoints:** Model parameter checkpoints are saved to [`checkpoints/physically_corrected/checkpoint.pt`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/checkpoints/physically_corrected/checkpoint.pt) and evaluated repeatably.
