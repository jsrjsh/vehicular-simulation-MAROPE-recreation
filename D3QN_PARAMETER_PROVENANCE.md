# D3QN_PARAMETER_PROVENANCE.md

This document traces the origin of all Dueling Double DQN and Prioritized Experience Replay hyperparameters to identify whether they are specified by the **Recreation Guide**, the **Manuscript**, or are **Engineering Assumptions**.

---

## 1. Parameter Provenance Matrix

| Hyperparameter | Value | Primary Source | Provenance Analysis & Documentation |
| :--- | :---: | :--- | :--- |
| **Safety-Task Action Mask** | `{1, 2, 3}` | Recreation Guide | Defined in Section 1.4: *"Safety tasks mask actions {1,2,3} (LTE) in the policy..."* and Section 5: *"9. Safety task: actions {1, 2, 3} masked in policy (not env step)."* |
| **Replay Capacity** | `10,000` | Recreation Guide | Specified in Section 3.1: *"buffer \| 10,000"*. |
| **Learning Rate** | `1e-3` | Recreation Guide | Specified in Section 3.1: *"Adam lr \| 1e-3"*. |
| **Target Update Interval** | `100` steps | Recreation Guide | Specified in Section 3.1: *"target update \| every 100 steps"*. |
| **Huber Loss (Smooth L1)** | Smooth L1 | Recreation Guide | Specified in Section 3.1: *"loss \| Smooth L1, grad clip 10"*. |
| **Batch Size** | `32` | Recreation Guide | Specified in Section 3.1: *"batch \| 32"*. |
| **Discount Factor ($\gamma$)** | `0.95` | Recreation Guide | Specified in Section 3.1: *"γ (discount) \| 0.95"*. |
| **Epsilon Schedule** | `1.0 -> 0.05` | Recreation Guide | Specified in Section 3.1: *"ε (explore) \| 1.0 -> 0.05, decay 2000 steps (exp)"*. |
| **PER Exponent ($\alpha$)** | `0.6` | Recreation Guide | Specified in Section 3.1: *"PER \| α=0.6, β: 0.4->1.0 over 50k steps"*. |
| **PER Correction ($\beta$)** | `0.4 -> 1.0` | Recreation Guide | Specified in Section 3.1: *"PER \| α=0.6, β: 0.4->1.0 over 50k steps"*. |
| **Priority Epsilon** | `1e-6` | Engineering Assumption | A small constant added to TD-errors to prevent transitions from having a sampling probability of absolute zero. No value is specified in the guide; the industry standard $1\text{e-}6$ is assumed. |
| **Optimizer Type** | Adam | Recreation Guide | Specified in Section 3.1: *"Adam lr \| 1e-3"*. |
| **Gradient Clipping Norm** | `10.0` | Recreation Guide | Specified in Section 3.1: *"loss \| Smooth L1, grad clip 10"*. |
| **Target Update Method** | Hard Copy | Engineering Assumption | The update frequency *"every 100 steps"* implies hard state dict copying, as soft target averaging ($\tau$) is typically performed on every gradient step. |
| **Beta Annealing Profile** | Linear | Engineering Assumption | Annealing $\beta$ from $0.4 \to 1.0$ over 50,000 steps is implemented linearly ($\Delta \beta = \frac{0.6}{50000}$ per sample step) matching standard RL practices. |

---

## 2. In-Depth Documentation of Assumptions

1. **Target Update Method:** Soft target updating ($\theta_{\text{target}} \leftarrow \tau \theta_{\text{online}} + (1-\tau)\theta_{\text{target}}$) is commonly used in continuous control (DDPG/SAC), whereas discrete Q-learning defaults to hard updating at periodic intervals. A hard copy of state dicts is assumed at every $100$ gradient updates.
2. **Priority Epsilon ($\epsilon_p = 1\text{e-}6$):** Used in the formula $p_i = |\text{TD\_error}_i| + \epsilon_p$ to prevent transitions with zero TD error from having zero priority, which would block them from ever being sampled again.
3. **Replay Buffer Structure:** Implemented as a ring buffer with flat NumPy arrays for priorities, which is extremely robust and fast for $N=10,000$ transitions.
