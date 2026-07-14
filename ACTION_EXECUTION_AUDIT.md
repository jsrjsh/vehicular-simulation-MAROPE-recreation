# ACTION_EXECUTION_AUDIT.md

This document audits action mapping coordinates, safety task policy masking, and the SINR-proportional offloading ratio adaptation.

---

## 1. Action Mapping Parity

The action mapping table maps each action index $a \in [0, 10]$ to a target RAT index and offloading fraction $\rho$:

* **NoOffload (Action 0):** Maps to `rat_idx = 0`, `rho = 0.0` (pure local computing).
* **AllOffload (Action 8):** Maps to `rat_idx = 4` (5G-NR), `rho = 1.0` (100% offloading).
* **Safety Task Policy Mask:** Masks actions $\{1, 2, 3\}$ (which offload to LTE, `rat_idx = 1`), preventing safety tasks from using the high-latency LTE channel.

---

## 2. Sampled Step Trace (N=8 URLLC)

Below is a step trace logging the action mapping, SINR values, calculated $q_r$ ratio, and final adapted offloading ratio $\rho'$ for a single vehicle step:

```
[Agent 0 Step Trace]
- Chosen Action: 8 (5G-NR 100%)
- Nominal rho: 1.00
- Nearest RSU Dist: 245.3 m
- Link SINRs (dB):
  - LTE (RAT 1): 27.24 dB   -> Linear Gamma: 529.66
  - ITS-G5 (RAT 2): 21.05 dB -> Linear Gamma: 127.35
  - WiFi-6 (RAT 3): 14.50 dB -> Linear Gamma: 28.18
  - 5G-NR (RAT 4): 25.10 dB  -> Linear Gamma: 323.59
- Sum of Gammas: 529.66 + 127.35 + 28.18 + 323.59 = 1008.78
- 5G-NR SINR Ratio (q_r): 323.59 / 1008.78 = 0.3208
- Adapted Offloading Ratio (rho'): clip(1.0 * 0.3208, 0, 1) = 0.3208
```

---

## 3. Findings

### 3.1 SINR-Proportional Throttling
* **Core Discovery:** Because the sum of linear SINRs ($\sum_{k=1}^4 \gamma_k$) aggregates all 4 wireless interfaces, the individual RAT ratio $q_r = \frac{\gamma_r}{\sum \gamma_k}$ is mathematically bounded by $1.0$. If all 4 links are active with similar channel qualities, $q_r$ is roughly $0.25 - 0.35$.
* **Impact on Offloading:** Even when the agent selects full offloading ($\rho = 1.0$), the environment clips the adapted offloading ratio $\rho'$ to $0.32$, forcing $68\%$ of the workload to run locally. This explains why the mean queue delay remains low and why energy consumption scales down in corrected mode.
* **Safety Action Masking:** Safety tasks successfully mask out actions $\{1, 2, 3\}$ in policy action selection, keeping LTE offloading at $0\%$.
