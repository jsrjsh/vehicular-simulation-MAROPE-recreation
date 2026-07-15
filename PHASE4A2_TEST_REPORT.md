# PHASE4A2_TEST_REPORT.md

This document logs the execution outcomes of the Phase 4A.2 regression unit tests.

---

## 1. Regression Test Invariants Verified
* **Fixed AllOffload $\rho=1.0$ Bypass:** Verified that setting `policy_type="alloffload"` locks the adapted ratio $\rho'$ to exactly $1.0$ under deep fading.
* **Fixed NoOffload $\rho=0.0$ Bypass:** Confirmed adapted ratio remains $0.0$.
* **Adaptive $\rho$ Modulation:** Verified that learned policy actions undergo SINR-proportional scaling.
* **Metric Denominator Semantics:** Checked step-level ($0.09$ J) vs active-task ($0.15$ J) average denominators.
* **Seed aggregation math:** Confirmed mean and standard deviation logic.
* **Mode separation directories:** Confirmed results output folders.
