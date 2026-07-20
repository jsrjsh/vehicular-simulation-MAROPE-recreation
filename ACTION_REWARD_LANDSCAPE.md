# ACTION REWARD LANDSCAPE COMPARISON

This document compares the deterministic step reward for the valid actions across task types under the two energy formulations: `energy_legacy_unconverted` (mJ directly added to J) and `energy_si_corrected` (mJ properly converted to J).

---

## 1. Safety Task Landscape
**State context:** 0.1 MB, 50 ms local latency, D=100ms, $\alpha=0.7, \beta=0.3$.
* **Local CPU Energy:** 0.05 J. **Reward (Local):** 0.9360
* **5G AllOffload Tx Energy:**
  * **Legacy (unconverted):** 0.08 J (Added as 0.08).
  * **SI Corrected:** 0.00008 J.
* **Impact of correction:** Almost zero. Safety tasks are extremely small (0.1 MB). Even the bugged "mJ-as-J" formulation only adds 0.08 J. $e^{-0.08/3}$ is still close to 1.0. Local execution dominates due to the hidden PRR=1 convention regardless of energy mode.

---

## 2. Infotainment Task Landscape
**State context:** 2.0 MB, 250 ms local latency, D=500ms, $\alpha=0.4, \beta=0.6$.
* **Local CPU Energy:** 0.25 J. **Reward (Local):** 0.8359
* **ITS-G5 AllOffload Tx Energy:**
  * **Legacy:** 4.0 J. $e^{-4.0/3} = 0.26$. **Reward (Offload):** 0.8055
  * **SI Corrected:** 0.004 J. $e^{-0.004/3} = 0.998$. **Reward (Offload):** 0.8070
* **Impact of correction:** Minimal. While the energy penalty drops massively under SI correction, Infotainment tasks still receive a huge utility boost from the $PRR=1$ local execution convention. The mathematical boost of local reliability out-scales the savings in transmission energy.

---

## 3. Compute Task Landscape
**State context:** 5.0 MB, 1000 ms local latency, D=1000ms, $\alpha=0.2, \beta=0.8$.
* **Local CPU Energy:** 2.0 J. **Reward (Local):** 0.5525
* **5G AllOffload Tx Energy:**
  * **Legacy:** 4.0 J. $e^{-4.0/3.0} \approx 0.26$. **Reward (Offload):** 0.5385
  * **SI Corrected:** 0.004 J. $e^{-0.004/3.0} \approx 0.998$. **Reward (Offload):** 0.5413
* **Impact of correction:** 
  * Under the legacy formulation, 5G Offload was strictly **worse** than Local (0.5385 vs 0.5525) purely due to the 4.0 Joules penalty crushing the energy reward term.
  * Under the SI corrected formulation, 5G Offload energy penalty vanishes (0.004 J). However, due to queueing delays, the latency term degrades, keeping the overall reward near 0.5413. 
  * **Key takeaway:** Even with the energy unit perfectly fixed, the reward for Compute Offload (0.5413) STILL cannot surpass the reward for Local execution (0.5525). The PRR=1 local convention mathematically dominates the environment.

---

## 4. Overall Conclusion on Reward Landscape
Correcting the transmission energy unit to Joules behaves exactly as expected physically—it makes offloading large tasks incredibly energy-efficient. However, because local tasks are hard-coded to achieve $PRR=1$, the local action receives a massive $+ \alpha \times 1.0$ guaranteed reliability bonus. The mathematical reward scale is structurally unbalanced: no amount of energy savings can overcome the reliability gap enforced by the local execution branch.
