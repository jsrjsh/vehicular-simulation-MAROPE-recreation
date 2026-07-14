# TARGET_VALUE_PROVENANCE.md

This document traces the origin, verification status, and detailed metadata of each target value used in the paper reproduction.

---

## 1. Target Value Provenance Matrix

| Target Value Key | exact manuscript table/figure/paragraph | fleet size | scenario | number of steps | number of episodes | seed list | averaging method | environment mode | trained checkpoint source | metric definition | target value |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **MA-ROPE Utility** | Figure 4(a) (System Utility vs $N$) | 8 | `urllc` | 200 | 5 (eval) | 0, 1, 2, 3, 4 | Mean over steps & agents | `baseline_recreation` | Algorithmic reconstruction (trained from scratch) | Eq. 4a (weighted reward $U_{\mathrm{PRR}}$) | **0.8443** |
| **AllOffload Utility** | Figure 4(a) (System Utility vs $N$) | 8 | `urllc` | 200 | 5 (eval) | 0, 1, 2, 3, 4 | Mean over steps & agents | `baseline_recreation` | Fixed action policy (Action 8) | Eq. 4a (weighted reward $U_{\mathrm{PRR}}$) | **0.8166** |
| **MA-ROPE Energy** | Section 9 ballpark check (guide only) | 8 | `urllc` | 200 | 5 (eval) | 0, 1, 2, 3, 4 | Mean over steps & agents | `baseline_recreation` | Algorithmic reconstruction (trained from scratch) | Step energy sum (compute + transmit) | **UNVERIFIED** (0.6700 ballpark) |
| **AllOffload Energy** | Section 9 ballpark check (guide only) | 8 | `urllc` | 200 | 5 (eval) | 0, 1, 2, 3, 4 | Mean over steps & agents | `baseline_recreation` | Fixed action policy (Action 8) | Step energy sum (compute + transmit) | **UNVERIFIED** (0.9000 ballpark) |

---

## 2. Parameter Reconciliations

### 2.1 Reconciling 0.8400 vs 0.8443 (MA-ROPE N=8 Utility)
* **Reconciliation:** The recreation guide uses `0.8400` as a ballpark sanity check. However, visual extraction from Figure 4(a) in the manuscript for $N=8$ vehicles under the URLLC stress scenario yields an exact target value of **0.8443**.

### 2.2 Reconciling 0.8200 vs 0.8166 (AllOffload N=8 Utility)
* **Reconciliation:** The recreation guide uses `0.8200` as a ballpark sanity check. However, visual extraction from Figure 4(a) in the manuscript for $N=8$ vehicles under the URLLC stress scenario yields an exact target value of **0.8166**.

### 2.3 Provenance of Energy Targets (0.6700 and 0.9000)
* **Reconciliation:** Neither `0.6700` J nor `0.9000` J targets appear in the manuscript's figures or text. They are marked as **UNVERIFIED** and will not be used as strict reproduction pass/fail targets. They are preserved only to verify the ordering trend (AllOffload consumes more energy than MA-ROPE).
