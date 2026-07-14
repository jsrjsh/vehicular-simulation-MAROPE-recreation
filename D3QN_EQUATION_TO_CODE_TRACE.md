# D3QN_EQUATION_TO_CODE_TRACE.md

This document traces every neural network, optimization, and action-selection equation for the Dueling Double DQN agent layer from the [`MA_ROPE_RECREATION_GUIDE.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/MA_ROPE_RECREATION_GUIDE.md) to its implementation in the source code and its validation in the unit test suite.

---

## Traceability Index

| Scientific Equation / Operation | Source File | Class / Function | Target Unit / Shape | Verification Test Name | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dueling Recombination**<br>$Q(s, a) = V(s) + A(s, a) - \text{mean}_{a'}(A(s, a'))$ | [`agents/d3qn/network.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/network.py) | `DuelingQNetwork.forward` | Tensor Shape: `(batch, 11)` | `test_recombination` | **Verified** |
| **Double DQN Target Value**<br>$y = r + \gamma Q_{\text{target}}(s', \text{argmax}_{a'} Q_{\text{online}}(s', a')) \cdot (1-d)$ | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent.learn` | Scalar / Float | `test_double_dqn_target_calculation` | **Verified** |
| **Safety Task Policy Action Masking**<br>$Q(s, a_{\text{LTE}}) \leftarrow -\infty$ | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent.select_action`, `D3QNAgent.learn` | Dimensionless | `test_learning_fixture`, `test_double_dqn_target_calculation` | **Verified** |
| **Epsilon Exploration Decay**<br>$\epsilon = \max(\epsilon_{\text{end}}, \epsilon_{\text{start}} \cdot e^{-\text{step}/\tau})$ | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent.decay_epsilon` | Probability $[0.05, 1.0]$ | `test_epsilon_greedy_boundary` | **Verified** |
| **Huber Loss (Smooth L1)**<br>$\mathcal{L}_{\delta}(a) = \text{Huber}(Q_{\text{online}}(s, a), y)$ | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent.learn` | Scalar Loss | `test_loss_and_gradient_bounds` | **Verified** |
| **Gradient Norm Clipping**<br>$\text{clip}(\|\nabla_{\theta} \mathcal{L}\|_2, 10.0)$ | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent.learn` | Gradient Norm | `test_loss_and_gradient_bounds` | **Verified** |
| **Hard Target Update**<br>$\theta_{\text{target}} \leftarrow \theta_{\text{online}}$ | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent.update_target_network` | Network Parameters | `test_online_target_network_independence` | **Verified** |
| **State Input Space**<br>12-dimensional normalized vector | [`agents/d3qn/network.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/network.py) | `DuelingQNetwork` | Input Shape: `(batch, 12)` | `test_network_shapes` | **Verified** |
| **Action Output Space**<br>11 discrete action indices | [`agents/d3qn/network.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/network.py) | `DuelingQNetwork` | Output Shape: `(batch, 11)` | `test_network_shapes` | **Verified** |
