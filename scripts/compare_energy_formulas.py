# scripts/compare_energy_formulas.py
"""
Deterministic comparison of the energy formulas for a single URLLC Safety Task offloaded via 5G-NR.
Evaluates:
- task data = 0.1 MB
- local cycles = 1e8
- local CPU freq = 2e9 Hz (c_ratio = 0.05)
- action = 8 (5G-NR, rho = 1.0)
- 5G-NR tx power/energy coeff = 0.8 mJ
- latency L = 10.0 ms
"""

import math

def main():
    # Constant inputs
    P_CPU_W = 2.0
    CPU_FREQ_HZ = 2e9
    c_ratio = 1e8 / CPU_FREQ_HZ  # 0.05
    D_ms = 100.0
    rho = 1.0
    tx_energy_mj = 0.8  # 5G NR
    data_mb = 0.1
    L_total = 10.0  # ms
    
    print("Evaluating URLLC Safety Task (5G-NR, rho=1.0, L=10ms):")
    
    # 1. Literal Recreation Guide Formula (Log-based)
    rho_prime = 1.0 - 1e-9
    term1 = P_CPU_W * math.log10(c_ratio)
    term2 = tx_energy_mj * math.log10(D_ms / (1.0 - rho_prime))
    term3 = 1.0 * rho_prime * math.log10(rho_prime)
    e_literal = term1 + term2 + term3
    
    # 2. Current Physically Corrected Formula
    e_tx = (tx_energy_mj * data_mb * 1.0) / 1000.0
    e_corrected = P_CPU_W * (L_total / 1000.0) + e_tx
    
    # 3. Manuscript Equation (Log-based LaTeX rendering)
    e_manuscript = term1 + term2
    
    # 4. Implemented Source Code (baseline_recreation mode)
    c_ratio_clamp = max(c_ratio, 1e-9)
    term1_code = P_CPU_W * math.log10(c_ratio_clamp)
    term2_code = tx_energy_mj * math.log10(max(D_ms / max(1.0 - rho_prime, 1e-9), 1e-9))
    term3_code = 1.0 * rho_prime * math.log10(max(rho_prime, 1e-9))
    e_code_baseline = term1_code + term2_code + term3_code
    
    print(f"Literal Recreation Guide: {e_literal:.4f} J")
    print(f"Physically Corrected: {e_corrected:.4f} J")
    print(f"Manuscript Log-based: {e_manuscript:.4f} J")
    print(f"Implemented Baseline Recreation Code: {e_code_baseline:.4f} J")
    
    # Write to ENERGY_FORMULA_COMPARISON.md
    content = """# ENERGY_FORMULA_COMPARISON.md

This document compares the numerical outcomes of the four energy calculation formulas for a single deterministic URLLC Safety Task offloaded via 5G-NR.

---

## 1. Parameters of Deterministic Task
* **Task Type:** Safety
* **Data Size:** 0.1 MB
* **Local CPU Cycles:** $10^8$ cycles
* **Local CPU Frequency ($f_{\\mathrm{cpu}}$):** 2.0 GHz
* **Local CPU Power ($P_{\\mathrm{cpu}}$):** 2.0 W
* **Total Latency ($L_{\\mathrm{total}}$):** 10.0 ms
* **Offloading Ratio ($\\rho$):** 1.0 (5G-NR)
* **5G-NR Tx Coefficient ($E_{\\mathrm{tx}}$):** 0.8 mJ

---

## 2. Numerical Comparison Table

| Formula Source | Mathematical Formulation | Numerical Result (Joules) | Analysis & Observations |
| :--- | :--- | :---: | :--- |
| **Literal Recreation Guide** | $P_{\\mathrm{cpu}} \\cdot \\log_{10}(C/f) + E_{\\mathrm{tx}} \\cdot \\log_{10}(D/(1-\\rho)) + \\rho \\cdot \\log_{10}(\\rho)$ | **VAL_LITERAL J** | Log terms create negative values for compute, offset by large positive transmission log. |
| **Physically Corrected** | $P_{\\mathrm{cpu}} \\cdot \\frac{L_{\\mathrm{total}}}{1000} + \\frac{E_{\\mathrm{tx}} \\cdot D \\cdot \\rho}{1000}$ | **VAL_CORRECTED J** | Linear physical representation of CPU energy over time + transmission radio energy. |
| **Manuscript Equation** | $P_{\\mathrm{cpu}} \\cdot \\lg(C/f) + P_{\\mathrm{tx}} \\cdot \\lg(D/(1-\\rho))$ | **VAL_MANUSCRIPT J** | Matches literal guide log terms without the regularization entropy term. |
| **Implemented Source Code** | `baseline_recreation` code block | **VAL_CODE J** | Matches the guide's literal log-based equations with clamping controls. |

---

## 3. Discrepancy Reconciliation

* **Why the Log Formulas Diverge:**
  The log-based formulations ($P_{\\mathrm{cpu}} \\cdot \\log_{10}(C/f)$) compute negative energy values because the computation duration $C/f$ is typically small (e.g. 0.05 seconds). 
  At the same time, the communication term ($E_{\\mathrm{tx}} \\cdot \\log_{10}(D/(1-\\rho))$) goes to positive infinity as $\\rho \\to 1$. 
  Because these log-based terms do not represent real physical energy consumption, they produce arbitrary values that do not correspond to the actual physical power profile of the device.
* **Why the Corrected Formula is Accurate:**
  The `physically_corrected` formula treats energy linearly: power multiplied by active compute time plus the radio energy spent transmitting. This maps directly to physical Joules.
"""
    content = content.replace("VAL_LITERAL", f"{e_literal:.4f}")
    content = content.replace("VAL_CORRECTED", f"{e_corrected:.4f}")
    content = content.replace("VAL_MANUSCRIPT", f"{e_manuscript:.4f}")
    content = content.replace("VAL_CODE", f"{e_code_baseline:.4f}")
    
    with open("ENERGY_FORMULA_COMPARISON.md", "w") as f:
        f.write(content)
    print("ENERGY_FORMULA_COMPARISON.md written.")

if __name__ == "__main__":
    main()
