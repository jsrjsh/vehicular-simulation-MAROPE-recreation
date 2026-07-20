# LOCAL-EXECUTION RELIABILITY SEMANTICS

This document traces the exact definition and usage of the Packet Reception Ratio (PRR) when an agent chooses local execution (`rho = 0`, meaning no transmissions occur, so `n_tx = 0`).

## 1. The Core Ambiguity (0/0 Problem)
When a vehicle executes a task locally, it does not transmit any packets over the network. 
The mathematical definition of PRR is:
$PRR = \frac{n_{rx}}{n_{tx}}$
When $n_{tx} = 0$, this fraction evaluates to $0/0$ (undefined). 

## 2. Trace Across Sources

### A. Manuscript Definition
* The manuscript defines PRR based on successfully transmitted and received packets. A strict reading implies it is only defined for transmitted packets. 
* However, the manuscript simultaneously reports that the `NoOffload` policy achieves a $U_{PRR}$ (System Utility) of **0.8442** (at N=32). 
* Since the $\alpha \cdot PRR$ term accounts for the vast majority of the reward (e.g., up to $0.7$ for Safety tasks), a $U_{PRR}$ of $0.84$ is mathematically impossible unless the manuscript treats local execution PRR as $1.0$ when calculating the reward.

### B. Recreation Guide
* The guide states in Section 2.12 (Observation): `if no samples for that RAT: 0.5 if any global tx else 1.0`.
* In Section 2.10 (Reward): `Use empirical PRR (not OTR) in step(.), α⋅β from task table.` It does not explicitly state what to substitute for local execution in the reward formula.

### C. Environment Implementation (`env/environment.py`)
* The environment resolves the $0/0$ problem at lines 330-331:
  ```python
  if rat_idx == 0 or rho_prime == 0.0:
      prr_val = 1.0
  ```
* **Status:** In our simulator, local execution unconditionally receives **PRR = 1.0** in the step reward.

### D. Metric Implementation & Training Logs
* In `reproduce_paper_sweeps.py` and `evaluate_marope_calibrated.py`, the reported metric `u_prr` is simply the average of the step rewards ($U$).
* Since the step reward uses PRR = 1.0 for local execution, the reported $U_{PRR}$ for `NoOffload` incorporates this 1.0 value, leading to the high $0.84$ utility score.
* Conversely, the Fleet OTR (On-Time Ratio) metric implementation checks `tx > 0`. If `tx = 0` (NoOffload), it evaluates to `0.0`. 

## 3. Conclusion
Local execution receives a **PRR = 1.0** in the training reward and $U_{PRR}$ evaluations, while simultaneously receiving **OTR = 0.0** in the evaluation metrics. This asymmetric semantic choice guarantees that local execution receives the maximum possible reliability reward without appearing as "successful transmissions" in the network statistics.
