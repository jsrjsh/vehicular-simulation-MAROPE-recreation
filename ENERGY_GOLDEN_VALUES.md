# ENERGY GOLDEN VALUES (SI CORRECTED)

This document contains exact hand-calculations for task energy and reward terms under the `energy_si_corrected` mathematical formulation, ensuring 1 mJ = $10^{-3}$ J.

**Universal Formulae:**
* Local Energy: $E_{local} = 2.0 \cdot (L_{local} / 1000) \cdot (1 - \rho)$ Joules
* Transmission Energy: $E_{tx} = (\text{tx\_energy\_mj} \cdot \text{Data\_MB} \cdot \rho) / 1000$ Joules
* Total Energy: $E_{total} = E_{local} + E_{tx}$ Joules
* Reward Term: $e^{-E_{total} / 3.0}$

---

## 1. Safety Task (0.1 MB, 50 ms local execution, LTE offload at $\rho=0.5$)
* **Action:** LTE 50% (Action 2). LTE `tx_energy_mj` = 1.5 mJ/MB.
* **Local CPU Energy:** $2.0 \cdot (50 / 1000) \cdot 0.5 = 2.0 \cdot 0.05 \cdot 0.5 = \mathbf{0.05 \text{ J}}$
* **Partial-Offload Tx Energy:** $(1.5 \cdot 0.1 \cdot 0.5) / 1000 = 0.075 \text{ mJ} = \mathbf{0.000075 \text{ J}}$
* **Total Energy:** $0.05 + 0.000075 = \mathbf{0.050075 \text{ J}}$
* **Reward Term ($e^{-E/3}$):** $e^{-0.050075 / 3.0} = e^{-0.01669} \approx \mathbf{0.9834}$

---

## 2. Infotainment Task (2.0 MB, 250 ms local execution, ITS-G5 offload at $\rho=1.0$)
* **Action:** ITS-G5 100% (Action 5 equivalent with $\rho=1.0$). ITS-G5 `tx_energy_mj` = 2.0 mJ/MB.
* **Local CPU Energy:** $2.0 \cdot 0.25 \cdot (0.0) = \mathbf{0.0 \text{ J}}$
* **Full-Offload Tx Energy:** $(2.0 \cdot 2.0 \cdot 1.0) / 1000 = 4.0 \text{ mJ} = \mathbf{0.004 \text{ J}}$
* **Total Energy:** $0.0 + 0.004 = \mathbf{0.004 \text{ J}}$
* **Reward Term ($e^{-E/3}$):** $e^{-0.004 / 3.0} = e^{-0.00133} \approx \mathbf{0.9987}$

---

## 3. Compute Task (5.0 MB, 1000 ms local execution, 5G offload at $\rho=1.0$)
* **Action:** 5G 100% (Action 8). 5G `tx_energy_mj` = 0.8 mJ/MB.
* **Local CPU Energy:** $2.0 \cdot 1.0 \cdot (0.0) = \mathbf{0.0 \text{ J}}$
* **Full-Offload Tx Energy:** $(0.8 \cdot 5.0 \cdot 1.0) / 1000 = 4.0 \text{ mJ} = \mathbf{0.004 \text{ J}}$
* **Total Energy:** $0.0 + 0.004 = \mathbf{0.004 \text{ J}}$
* **Reward Term ($e^{-E/3}$):** $e^{-0.004 / 3.0} = e^{-0.00133} \approx \mathbf{0.9987}$

---

*(Note: Under the legacy, un-converted formulation, the Compute task's Tx Energy would be computed as $4.0$ Joules, causing the reward term to crash to $e^{-4/3} \approx 0.2636$. By correcting the unit, offloading a 5MB task becomes practically "free" in energy compared to local execution.)*
