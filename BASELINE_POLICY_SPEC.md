# BASELINE_POLICY_SPEC.md

This document defines the execution rules and design requirements for the fixed baseline policies.

---

## 1. Fixed Policy Semantic Rules

### 1.1 NoOffload Policy (Action 0)
* **Execution Rule:** All tasks are executed locally.
* **Link Selection:** `rat_idx = 0` (Local).
* **Offloading Ratio:** $\rho' = 0.0$.
* **Bypass:** Bypasses SINR-proportional adaptation. No transmissions occur, meaning link counters and transmit energy remain at zero.

### 1.2 AllOffload Policy (Action 8)
* **Execution Rule:** All tasks are offloaded to the nearest RSU via 5G-NR.
* **Link Selection:** `rat_idx = 4` (5G-NR).
* **Offloading Ratio:** $\rho' = 1.0$.
* **Bypass Rule:** Bypasses SINR-proportional adaptation. The adapted ratio $\rho'$ must remain exactly $1.0$, rather than being throttled by link quality divisions.

---

## 2. Implementation Architecture

To support the fixed policy bypass, we introduce an `env_mode` configuration in the environment:
* In `baseline_recreation` or `physically_corrected` mode:
  * If the global environment's active execution mode is configured as `alloffload` or `nooffload` (rather than `full` learned agent mode), the environment bypasses the SINR-proportional clipping logic in `env/environment.py`.
  * The environment detects the policy type and applies the forced values:
    * If policy is `alloffload`: `adapted_rhos[i] = 1.0` and `rat_idx = 4` for all active vehicles.
    * If policy is `nooffload`: `adapted_rhos[i] = 0.0` and `rat_idx = 0` for all active vehicles.
  * This is flagged in the returned info dictionary under the key `"policy_type"`.
