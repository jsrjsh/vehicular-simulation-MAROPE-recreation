# FEDAVG_EQUATION_TO_CODE_TRACE.md

This document traces every mathematical formula and workflow operation for Synchronous Federated Averaging (FedAvg) from the [`MA_ROPE_RECREATION_GUIDE.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/MA_ROPE_RECREATION_GUIDE.md) to its implementation in the source files and its validation in the unit test suite.

---

## Traceability Index

| FedAvg Equation / Operation | Source File | Class / Function | Target Unit / Shape | Verification Test Name | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FedAvg Weighted Sum**<br>$w_{\text{global}} = \sum_{i} \left( \frac{n_i}{\sum_j n_j} \right) w_i$ | [`agents/federated/fedavg.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/fedavg.py) | `federated_averaging` | State Dict weights | `test_weighted_averaging_two_agents_hand_calculated`, `test_parameter_shape_and_key_validation` | **Verified** |
| **Participation Threshold**<br>$\frac{\|S_{\text{active}}\|}{N} \ge 0.70$ | [`agents/federated/coordinator.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/coordinator.py) | `FederatedCoordinator.aggregate_and_broadcast` | Dimensionless fraction | `test_participation_threshold_boundaries` | **Verified** |
| **Global Model Broadcast**<br>$\theta_{i} \leftarrow w_{\text{global}}$ | [`agents/federated/coordinator.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/coordinator.py) | `FederatedCoordinator.aggregate_and_broadcast` | State Dict weights | `test_global_broadcast_consistency_and_target_sync` | **Verified** |
| **Target Network Sync**<br>$\theta_{i, \text{target}} \leftarrow w_{\text{global}}$ | [`agents/federated/coordinator.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/coordinator.py) | `FederatedCoordinator.aggregate_and_broadcast` | State Dict weights | `test_global_broadcast_consistency_and_target_sync` | **Verified** |
| **Client Local Replay Isolations** | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent` | Memory references | `test_local_replay_buffers_remain_independent` | **Verified** |
| **Client Local Optimizers Isolations** | [`agents/d3qn/agent.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/d3qn/agent.py) | `D3QNAgent` | Memory references | `test_local_optimizers_remain_independent` | **Verified** |
| **Dropout / Exclude from Avg** | [`agents/federated/coordinator.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/coordinator.py) | `FederatedCoordinator.aggregate_and_broadcast` | State dict subsets | `test_participation_threshold_boundaries` | **Verified** |
| **Model Size Serialization** | [`agents/federated/coordinator.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/coordinator.py) | `FederatedCoordinator.__init__` | Bytes count | `test_global_broadcast_consistency_and_target_sync` | **Verified** |
