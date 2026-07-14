# LDP_EQUATION_TO_CODE_TRACE.md

This document traces every mathematical formula and workflow operation for Local Differential Privacy (LDP) from the [`MA_ROPE_RECREATION_GUIDE.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/MA_ROPE_RECREATION_GUIDE.md) to its implementation in the source files and its validation in the unit test suite.

---

## Traceability Index

| LDP Equation / Operation | Source File | Class / Function | Target Unit / Shape | Verification Test Name | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Client Update Difference**<br>$\Delta_i = w_i - w_{\text{global\_previous}}$ | [`agents/federated/coordinator.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/coordinator.py) | `FederatedCoordinator.aggregate_and_broadcast` | State Dict weights | `test_hand_calculated_2client_fixture` | **Verified** |
| **Global Update L2 Norm**<br>$\|\Delta_i\|_2 = \sqrt{\sum_j \|\Delta_{i,j}\|_2^2}$ | [`agents/privacy/gaussian_ldp.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/privacy/gaussian_ldp.py) | `apply_gaussian_ldp` | Float norm value | `test_global_vs_layer_clipping` | **Verified** |
| **Norm Clipping Scaling**<br>$\Delta_{\text{clipped}} = \Delta \cdot \min\left(1, \frac{C}{\|\Delta\|_2 + \eta}\right)$ | [`agents/privacy/gaussian_ldp.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/privacy/gaussian_ldp.py) | `apply_gaussian_ldp` | State Dict weights | `test_clipping_bounds`, `test_hand_calculated_2client_fixture` | **Verified** |
| **Gaussian Noise Addition**<br>$\text{noise} \sim \mathcal{N}(0, \sigma^2 C^2 I)$ | [`agents/privacy/gaussian_ldp.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/privacy/gaussian_ldp.py) | `apply_gaussian_ldp` | State Dict weights | `test_noise_statistics`, `test_hand_calculated_with_noise_samples` | **Verified** |
| **Nominal Epsilon Conversion**<br>$\sigma = \frac{\sqrt{2 \ln(1.25/\delta)}}{\epsilon}$ | [`scripts/train_federated.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/scripts/train_federated.py) | `main` | Float noise standard deviation | `test_hand_calculated_with_noise_samples` | **Verified** |
| **New Global Model Assembly**<br>$w_{\text{global\_new}} = w_{\text{global\_prev}} + \text{FedAvg}(\Delta_{i,\text{private}})$ | [`agents/federated/coordinator.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/coordinator.py) | `FederatedCoordinator.aggregate_and_broadcast` | State Dict weights | `test_hand_calculated_2client_fixture` | **Verified** |
| **Independence Seeding**<br>$\text{seed} = \text{base} + \text{client} + \text{round} \cdot 1000$ | [`agents/federated/coordinator.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/agents/federated/coordinator.py) | `FederatedCoordinator.aggregate_and_broadcast` | Integer seed | `test_seeding_independence` | **Verified** |
