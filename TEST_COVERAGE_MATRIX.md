# TEST_COVERAGE_MATRIX.md

This document maps all the mandatory test requirements specified in Phase 3A and Phase 3A.1 to the corresponding unit test implementations in [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py).

---

## 1. Coverage Matrix

| Required Verification Check | Target Unit Test Name | File Reference | Status |
| :--- | :--- | :--- | :---: |
| **Deterministic Repeatability** | `test_seed_repeatability` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **All 11 Action Mappings** | `test_action_mapping_all` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Observation Shape and Ordering** | `test_observation_ordering_and_properties` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Local Execution Latency** | `test_local_execution_latency`, `test_golden_costs_and_utility` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Full-Offload Latency** | `test_queue_delay_saturation`, `test_golden_costs_and_utility` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Each Partial-Offload Ratio** | `test_queue_delay_saturation` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Queue Saturation (Below/At/Above)** | `test_queue_delay_saturation` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **SINR Monotonicity with Distance** | `test_sinr_monotonicity` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Cellular Fading versus Speed** | `test_cellular_fading_speed` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **PRR Counter Correctness** | `test_prr_counter_correctness` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **OTR $\le$ PRR Invariant** | `test_otr_le_prr_invariant` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Utility Normalization ($[0, 1]$)** | `test_utility_normalization` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Energy Non-negativity** | `test_energy_non_negativity` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Reset/Step Interface Behavior** | `test_seed_repeatability`, `test_no_nan_or_infinite` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Invalid-Action Handling** | `test_invalid_action_handling` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **No NaN or Infinite Values** | `test_no_nan_or_infinite` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **PRR Initialization Rules** | `test_prr_initialization_defaults` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Golden Path Losses (LTE/ITS/WiFi/5G)** | `test_golden_path_losses` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Golden Wireless Links SINR** | `test_golden_wireless_links` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Golden Costs and Utility (PRR/OTR)** | `test_golden_costs_and_utility` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
| **Mode Configurations (Baseline vs Corrected)** | `test_mode_configurations` | [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py) | **PASSED** |
