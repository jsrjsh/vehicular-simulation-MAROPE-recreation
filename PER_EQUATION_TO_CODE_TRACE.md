# PER_EQUATION_TO_CODE_TRACE.md

This document traces every Prioritized Experience Replay (PER) equation and hyperparameter specified in [`MA_ROPE_RECREATION_GUIDE.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/MA_ROPE_RECREATION_GUIDE.md) to its corresponding implementation in the source files and its validation in the unit test suite.

---

## Traceability Index

| PER Equation / Operation | Source File | Class / Function | Target Unit / Shape | Verification Test Name | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sampling Probability**<br>$P(i) = \frac{p_i^{\alpha}}{\sum_k p_k^{\alpha}}$ | [`agents/d3qn/replay.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/replay.py) | `ReplayBuffer.sample` | Probability distribution $\sum_i P(i) = 1.0$ | `test_prioritization_sampling_bias`, `test_alpha_zero_uniform_approximation` | **Verified** |
| **Importance Sampling Weights**<br>$w_i = (N \cdot P(i))^{-\beta}$ | [`agents/d3qn/replay.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/replay.py) | `ReplayBuffer.sample` | Dimensionless weight float | `test_beta_weight_corrections` | **Verified** |
| **Weight Normalization**<br>$w'_i = \frac{w_i}{\max_j w_j}$ | [`agents/d3qn/replay.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/replay.py) | `ReplayBuffer.sample` | Normalized weight $w'_i \in [0.0, 1.0]$ | `test_beta_weight_corrections` | **Verified** |
| **Priority Update from TD Error**<br>$p_i = |\text{TD\_error}_i| + \epsilon_p$ | [`agents/d3qn/replay.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/replay.py) | `ReplayBuffer.update_priorities` | Float priority value | `test_priority_epsilon_guard`, `test_prioritization_sampling_bias` | **Verified** |
| **Beta Annealing Schedule**<br>$\beta_t = \min\left(1.0, 0.4 + t \cdot \frac{0.6}{50000}\right)$ | [`agents/d3qn/replay.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/replay.py) | `ReplayBuffer.sample` | Annealed exponent $\beta \in [0.4, 1.0]$ | `test_beta_weight_corrections` | **Verified** |
| **Weighted Huber Loss**<br>$\mathcal{L}_w = \frac{1}{B} \sum_i w'_i \cdot \text{Huber}(q_i, y_i)$ | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent.learn` | Scalar loss value | `test_weighted_loss_hand_calculation`, `test_loss_and_gradient_bounds` | **Verified** |
| **Ring Buffer Wraparound Alignment** | [`agents/d3qn/replay.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/replay.py) | `ReplayBuffer.add` | Capacity alignment | `test_buffer_insertion_and_wraparound` | **Verified** |
