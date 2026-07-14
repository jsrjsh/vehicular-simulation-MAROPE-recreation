# ENERGY_FORMULA_COMPARISON.md

This document compares the numerical outcomes of the energy calculation formulations and details the decomposed energy ledger for a deterministic task.

---

## 1. Parameters of Deterministic Task
* **Task Type:** URLLC Safety
* **Nominal Data Size:** 0.1 MB
* **Local CPU Cycles ($C$):** $10^8$ cycles
* **Local CPU Frequency ($f_{\mathrm{cpu}}$):** 2.0 GHz
* **Local CPU Power ($P_{\mathrm{cpu}}$):** 2.0 W
* **Offloading Ratio ($\\rho$):** 1.0 (5G-NR)
* **5G-NR Tx Coefficient ($E_{\mathrm{tx}}$):** 0.8 mJ

---

## 2. Decomposed Energy Ledger (Corrected Mode)

Here is the step-by-step energy breakdown for a single safety task offloaded via 5G-NR (Action 8) right under the RSU:

| Ledger Field | Value | Formula / Source |
| :--- | :---: | :--- |
| **Selected Action** | Action 8 | Action map selection |
| **Selected RAT** | 5G-NR (index 4) | Action map mapping |
| **Base $\\rho$** | 1.0 | Action map mapping |
| **Final SINR-adjusted $\\rho'$** | 0.3208 | $\\rho' = \\rho \\cdot \\frac{\\gamma_{\\mathrm{5G}}}{\\sum \\gamma_k}$ |
| **Task Data Size** | 0.1 MB | URLLC Safety Task Spec |
| **$L_{\\mathrm{tx}}$ before $\\rho$ scaling** | 1.0 ms | 5G-NR Spec latency |
| **Effective Transmitted Duration** | 1.0 ms | Offloading delay |
| **$P_{\\mathrm{tx}}$** | 23.0 dBm (200 mW) | Radio transmit power |
| **Radio Transmission Energy ($E_{\\mathrm{tx}}$)**| $2.566 \\times 10^{-5}$ J | $\\frac{E_{\\mathrm{tx\_coef}} \\cdot D \\cdot \\rho'}{1000}$ |
| **RAT Processing Energy** | 0.00 J | Negligible interface base cost |
| **Local Compute Energy** | 0.0679 J | $P_{\\mathrm{cpu}} \\cdot (1 - \\rho') \\cdot \\frac{C}{f_{\\mathrm{cpu}}}$ |
| **Idle / Waiting Energy** | 0.00 J | Vehicle active computing during time window |
| **Total Step Energy ($E$)** | **0.0679 J** | Sum of local compute + radio transmission energy |

---

## 3. Numerical Comparison Table

| Formula Source | Mathematical Formulation | Numerical Result (Joules) | Analysis & Observations |
| :--- | :--- | :---: | :--- |
| **Literal Recreation Guide** | $P_{\\mathrm{cpu}} \\cdot \\log_{10}(C/f) + E_{\\mathrm{tx}} \\cdot \\log_{10}(D/(1-\\rho)) + \\rho \\cdot \\log_{10}(\\rho)$ | **6.1979 J** | Log terms create negative values for compute, offset by large positive transmission log. |
| **Physically Corrected** | $P_{\\mathrm{cpu}} \\cdot \\frac{L_{\\mathrm{total}}}{1000} + \\frac{E_{\\mathrm{tx}} \\cdot D \\cdot \\rho}{1000}$ | **0.0201 J** | Linear physical representation of CPU energy over time + transmission radio energy. |
| **Manuscript Equation** | $P_{\\mathrm{cpu}} \\cdot \\lg(C/f) + P_{\\mathrm{tx}} \\cdot \\lg(D/(1-\\rho))$ | **6.1979 J** | Matches literal guide log terms without the regularization entropy term. |
| **Implemented Source Code** | `baseline_recreation` code block | **6.1979 J** | Matches the guide's literal log-based equations with clamping controls. |

---

## 4. Discrepancy Reconciliation

* **Why the Log Formulas Diverge:**
  The log-based formulations ($P_{\\mathrm{cpu}} \\cdot \\log_{10}(C/f)$) compute negative energy values because the computation duration $C/f$ is typically small (e.g. 0.05 seconds). 
  At the same time, the communication term ($E_{\\mathrm{tx}} \\cdot \\log_{10}(D/(1-\\rho))$) goes to positive infinity as $\\rho \\to 1$. 
  Because these log-based terms do not represent real physical energy consumption, they produce arbitrary values that do not correspond to the actual physical power profile of the device.
* **Why the Corrected Formula is Accurate:**
  The `physically_corrected` formula treats energy linearly: power multiplied by active compute time plus the radio energy spent transmitting. This maps directly to physical Joules.
