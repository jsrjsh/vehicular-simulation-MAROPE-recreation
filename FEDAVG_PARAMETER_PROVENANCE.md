# FEDAVG_PARAMETER_PROVENANCE.md

This document traces the origin of all Federated Learning (FedAvg) parameters to identify whether they are specified by the **Recreation Guide**, the **Manuscript**, or are **Engineering Assumptions**.

---

## 1. Parameter Provenance Matrix

| Hyperparameter | Value | Primary Source | Provenance Analysis & Documentation |
| :--- | :--- | :--- | :--- |
| **Number of Agents ($N$)** | `32` | Recreation Guide | Defined in Section 3.1: *"vehicles N \| 32"*. |
| **Local Training Duration** | `100` steps | Recreation Guide | Specified in Section 3.1: *"sync interval \| 100 steps"*. Each agent runs 100 local environment steps before submitting. |
| **Aggregation Interval** | `100` steps | Recreation Guide | Specified in Section 3.1: *"sync interval \| 100 steps"*. Aggregation occurs synchronously. |
| **Participation Threshold** | `70%` | Recreation Guide | Specified in Section 3.1: *"FedAvg participation \| 70% threshold"*. If active clients represent $< 70\%$ of the population, the round is aborted. |
| **Sample-Count Weighting** | $\frac{n_i}{\sum_j n_j}$ | Engineering Assumption | Standard FedAvg formula where client weights scale linearly with the count of local training samples ($n_i$) collected during the interval. |
| **Target Net Aggregation** | No | Engineering Assumption | Target network weights are not directly aggregated. Instead, the global aggregated online network weights $w_{\text{global}}$ are broadcast, and target networks synchronize locally post-broadcast. |
| **Optimizer State Aggregation** | No | Engineering Assumption | Client optimizer states (learning rates, momentum, Adam moment vectors) remain strictly local to prevent state corruption. |
| **Replay Buffers State** | Local | Recreation Guide / Spec | Explicit in guide: replay buffers remain local to each vehicle, preserving user privacy. |
| **Epsilon Schedule State** | Local | Engineering Assumption | Epsilon decay occurs locally for each agent based on its local training step counter, keeping exploration behaviors decoupled. |
| **Synchronization Timing** | Every 100 env steps | Recreation Guide | Tied directly to the synchronization interval parameter. |
| **Dropout / Non-participation** | Exclude from average | Engineering Assumption | If an agent is marked as dropped out, its local weights are excluded from that round's summation, and its weight contribution is zeroed. |

---

## 2. In-Depth Documentation of Assumptions

1. **Target Network Aggregation:** Averaging target networks independently can lead to slow convergence or parameter drift. The standard practice is to aggregate only the online networks, broadcast the global online parameters $w_{\text{global}}$, and then copy the online weights directly to target weights locally.
2. **Optimizer Reset:** When a global model is received, the client optimizer's momentum states are reset to zero to prevent the old local gradients from corrupting the newly synchronized global weights.
3. **Local Replay Buffers:** Replay buffers are local and never shared. This preserves the privacy constraints of the vehicular simulation platform.
