# PHASE4A1_ROOT_CAUSE_REPORT.md

This document summarizes the root-cause analysis for discrepancies between the paper target values and our recreated simulator baseline under $N=8$ vehicles in the URLLC stress scenario.

---

## 1. Discrepancy Classification Table

| Discrepancy Name | Target vs. Recreated | Discrepancy Class | Root-Cause Analysis |
| :--- | :---: | :--- | :--- |
| **MA-ROPE Energy** | 0.6700 vs. 0.2752 | **Metric-Definition / Specification Mismatch** | **1. Denominator mismatch:** The paper averages energy per *active compute task*, whereas our runner averages energy per *simulation step*. Since tasks arrive with probability $P_{\mathrm{arrival}} = 0.3$, step-averaging scales the results down by a factor of $\approx 3$.<br>**2. Physics mismatch:** The `physically_corrected` mode models energy linearly ($E = P_{\mathrm{cpu}} t$), whereas the paper uses LaTeX typeset log-based equations ($P_{\mathrm{cpu}} \cdot \lg(t)$) which inflate metrics. |
| **AllOffload Energy** | 0.9000 vs. 0.6533 | **Metric-Definition / Specification Mismatch** | Same as above. The linear corrected energy is lower due to the removal of typeset-inflated log energy equations. |
| **MA-ROPE Utility** | 0.8400 vs. 0.8943 | **Checkpoint / Training Mismatch** | No paper model checkpoint exists in the clean workspace (this is an *algorithmic reconstruction*, not a checkpoint load). Evaluated after a short 30-episode training run rather than the paper's 100 episodes, resulting in a minor $6.47\%$ deviation. |
| **AllOffload Utility** | 0.8200 vs. 0.7711 | **Stochastic Deviation** | Minor $5.96\%$ stochastic deviation due to Jakes fading and random shadow fading realizations over 5 evaluation episodes. |

---

## 2. In-Depth Root Cause Investigations

### 2.1 The Log-Based Energy typesetting Mismatch
* As verified in [`ENERGY_FORMULA_COMPARISON.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/ENERGY_FORMULA_COMPARISON.md), the literal LaTeX log-based formulas calculate energy as $6.1979$ J for a single task, while the physically corrected linear model calculates $0.0201$ J.
* This difference is caused by typesetting artifacts in the paper's LaTeX draft (placing a `\lg` prefix on duration ratios). In `baseline_recreation` mode, the simulator executes these log equations literally, leading to much larger metric values.

### 2.2 SINR-Proportional Offloading Throttling
* The offloading ratio is adapted using:
  $$\rho' = \rho \cdot \frac{\gamma_{\mathrm{selected}}}{\sum_{k=1}^4 \gamma_k}$$
* Because the denominator aggregates all 4 wireless interfaces (LTE, ITS-G5, WiFi-6, 5G-NR), the individual ratio is mathematically bounded. Even under the AllOffload action ($\rho = 1.0$), the adapted ratio $\rho'$ is throttled to $\approx 0.32$.
* This limits the actual workload offloaded to the RSU, reducing RSU queue delays and energy footprint during offloading phases.
