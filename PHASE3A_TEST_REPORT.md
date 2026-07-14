# PHASE3A_TEST_REPORT.md

This document logs the execution outcomes of the Phase 3A/3A.1 unit test suite, confirming the correctness and mathematical alignment of the MA-ROPE environment layer.

---

## 1. Test Execution Summary

* **Execution Date:** 2026-07-14
* **Python Version:** 3.9
* **Test Runner:** Standard `unittest`
* **Command Executed:** `python3 -m unittest discover -s tests`
* **Total Tests Executed:** 18
* **Total Passed:** 18
* **Total Failed:** 0
* **Total Errors:** 0
* **Status:** **PASS**

---

## 2. Detailed Test Results

| Test Case Name | Status | Verified Invariant / Criteria |
| :--- | :---: | :--- |
| `test_action_mapping_all` | **PASS** | Evaluated all 11 action indices; verified they map to the correct RAT index and offloading ratio $\rho$. |
| `test_seed_repeatability` | **PASS** | Verified that initializing two independent environments with seed 42 produces identical vehicle coordinates, speeds, battery percentages, tasks, and state transitions. |
| `test_observation_ordering_and_properties` | **PASS** | Checked that observation arrays are shape (12,) and float32. Confirmed normalized bounds $[0.0, 1.0]$. |
| `test_local_execution_latency` | **PASS** | Confirmed that local processing latency is exactly $\frac{C}{f_{\text{cpu}}} \times 1000$ ms. |
| `test_queue_delay_saturation` | **PASS** | Placed 4 vehicles on the same RSU, triggering different offloading actions; verified queue workload aggregates correctly below saturation ($Q=0.25$), at saturation ($Q=2.0$), and above saturation ($Q=4.0$). Checked queuing delay contribution ($12.5$ms, $100$ms, $200$ms respectively). |
| `test_sinr_monotonicity` | **PASS** | Confirmed that wireless link SINR decreases monotonically with distance ($d=10$m vs $d=100$m vs $d=1000$m). |
| `test_cellular_fading_speed` | **PASS** | Asserted that Jakes fading evaluates to $0.0$ for stationary vehicles ($v < 0.1$ m/s) and evaluates to a physical, non-negative fading loss at standard speeds. |
| `test_prr_counter_correctness` | **PASS** | Step through offloading actions; verified that transition outcomes correctly update the transmitted (`tx`) and received (`rx`) packet counters. |
| `test_otr_le_prr_invariant` | **PASS** | Verified that OTR is always less than or equal to PRR (since OTR requires successes to be on-time, while PRR has no latency constraint). |
| `test_utility_normalization` | **PASS** | Checked step rewards for multiple random steps; verified that the training utility $U_{\text{PRR}}$ is strictly bounded between $0.0$ and $1.0$. |
| `test_energy_non_negativity` | **PASS** | Confirmed that energy consumption values ($E$) are strictly non-negative. |
| `test_invalid_action_handling` | **PASS** | Asserted that attempting to pass invalid action indices ($a < 0$ or $a > 10$) raises a `ValueError`. |
| `test_no_nan_or_infinite` | **PASS** | Swept the environment for 50 steps; asserted that no observation values, rewards, or info dictionary metrics contain NaN or infinite values. |
| `test_prr_initialization_defaults` | **PASS** | Verified that PRR values initialize to $1.0$, and transition correctly to $0.5$ for unseen RATs once global offloading transmissions begin. |
| `test_golden_path_losses` | **PASS** | Asserted that computed path losses at reference $d=100.0$m match hand-calculated equations (LTE/ITS-G5 = 57.9 dB, WiFi-6 = 86.425175 dB, 5G-NR = 83.281361 dB) with high precision (up to 5 decimal places). |
| `test_golden_wireless_links` | **PASS** | Confirmed that under mocked shadowing ($0.0$ dB) and fading envelope ($A=1.0$), computed link SINRs match hand-calculated values (LTE = 75.1 dB, ITS-G5 = 55.1 dB). |
| `test_golden_costs_and_utility` | **PASS** | Checked local execution on a safety task; verified latency is exactly $50.0$ ms, energy is $0.10$ J, and reward $U_{\text{PRR}}$ matches hand-calculated $0.9361$. |
| `test_mode_configurations` | **PASS** | Verified that `baseline_recreation` mode correctly outputs log-based compute energy matching literal typesetting formulas, demonstrating negative energy boundaries. |

---

## 3. Key Mathematical Verification Highlights

### Toroidal Distance and Nearest RSU
* Vehicle position 500m and 1500m map correctly to RSU index 0 and 1.
* circular road wrap-around distance arithmetic holds: $d(10, 2590) = 20.0$ m.

### Saturation Queuing Latency
* Saturation load $Q = 4.0$ creates a queuing delay of exactly 200 ms.
* Low load $Q = 0.25$ creates a queuing delay of exactly 12.5 ms.
* Negative queuing delay is mathematically impossible.

### Energy Scale
* Local compute energy scales correctly with task cycles.
* Parallel-max total task duration dictates CPU idle energy consumption, matching the expected ~0.67 J and ~0.90 J benchmarks.
