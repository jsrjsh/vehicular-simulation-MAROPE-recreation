# ENERGY UNIT IMPACT REPORT

## 1. Manuscript Targets Comparison

We compare the Manuscript targets to the Greedy Oracle under both energy modes:

| Metric | Manuscript Target | Legacy (unconverted) | SI Corrected (mJ / 1000) | Conclusion on SI correction impact |
| :--- | :--- | :--- | :--- | :--- |
| **Energy (J)** | **0.7057** | 0.4773 | 0.4591 | **WORSENS CONSISTENCY**. Energy gap widens. |
| **Latency (ms)** | **213.0** | 235.5 | 229.5 | **IMPROVES CONSISTENCY**. Closer to 213 ms. |
| **System $U_{PRR}$** | **0.8323** | 0.8544 | 0.8515 | **IMPROVES CONSISTENCY**. Utility falls closer to 0.83. |

## 2. Verdict on the Defect
**CONFIRMED UNIT-CONVERSION DEFECT**
The mathematical use of `tx_energy_mj` in `env/environment.py` is undisputedly mathematically incorrect in standard edge computing simulations. It blindly adds milliJoules to Joules. This inflated offloading penalty prevented the RL agent from learning any meaningful offloading policy, causing the collapse to pure NoOffload behavior.

However, resolving this defect **IS INSUFFICIENT TO REPRODUCE THE POLICY**.
When the bug is fixed, the Greedy Oracle correctly offloads, which drives the total energy consumption *down* to **0.4591 J**. 
The manuscript reported **0.7057 J**.

Therefore, the manuscript's RL agent was using significantly more energy than an optimal Greedy policy would prescribe under the current mathematical rules.

## 3. What Does This Reveal?
If the paper achieved an energy signature of $0.70$ J, one of the following must be true of the original codebase:
1. **The original codebase contained the mJ bug.** The authors may have tuned their hyperparameters and run their tests with the mJ unit bug fully present, thereby inflating the reported total energy. 
2. **The Task Mix in the paper was different.** An environment consisting heavily of massive Compute tasks would naturally push both local and offload energy up toward 0.70 J.
3. **The RL formulation intentionally prioritized latency over energy.** The paper might have used a different weight formulation or scaled energy differently during RL training.
