# METRIC_DEFINITION_SPEC.md

This document defines the mathematical equations, numerators, and denominators for the evaluation metrics used to reproduce the paper and compare environment modes.

---

## 1. Metric Definitions

### 1.1 Energy Metrics
* **Energy per Step (`energy_per_step`):**
  Average energy consumed by a vehicle per simulation step:
  $$\text{Energy}_{\text{step}} = \frac{\sum_{t=1}^H E(t)}{H}$$
* **Energy per Active Task (`energy_per_active_task`):**
  Average energy consumed only on steps where a task was generated:
  $$\text{Energy}_{\text{active\_task}} = \frac{\sum_{t \in T_{\mathrm{active}}} E(t)}{|T_{\mathrm{active}}|}$$
  where $T_{\mathrm{active}}$ is the set of steps where a task was generated ($P_{\text{arrival}} = 0.3$).

---

### 1.2 Latency Metrics
* **Latency per Step (`latency_per_step`):**
  Average task completion latency per step:
  $$\text{Latency}_{\text{step}} = \frac{\sum_{t=1}^H L(t)}{H}$$
* **Latency per Active Task (`latency_per_active_task`):**
  Average task latency on steps where a task was generated:
  $$\text{Latency}_{\text{active\_task}} = \frac{\sum_{t \in T_{\mathrm{active}}} L(t)}{|T_{\mathrm{active}}|}$$

---

### 1.3 Communication & Queue Reliability
* **Packet Reception Ratio (PRR):**
  Ratio of successfully received packets to total transmitted packets over active wireless links:
  $$\text{PRR} = \frac{\sum_{t \in T_{\mathrm{tx}}} \mathbb{I}(\text{success}(t))}{|T_{\mathrm{tx}}|}$$
* **On-Time Ratio (OTR):**
  Ratio of packets successfully delivered before their deadline:
  $$\text{OTR} = \frac{\sum_{t \in T_{\mathrm{tx}}} \mathbb{I}(\text{success}(t) \land L(t) \le D(t))}{|T_{\mathrm{tx}}|}$$
* **Queue Loss Ratio:**
  Ratio of tasks dropped due to RSU queue backlogs:
  $$\text{QueueLoss} = \frac{\sum_{t \in T_{\mathrm{tx}}} \mathbb{I}(\text{Dropped}(t))}{|T_{\mathrm{tx}}|}$$

---

### 1.4 System Utility
* **Step-level Utility ($U_{\text{PRR}}$):**
  Average reward per step, including inactive steps:
  $$\text{Utility}_{\text{step}} = \frac{\sum_{t=1}^H U_{\mathrm{PRR}}(t)}{H}$$
* **Active-task Utility ($U_{\text{PRR, active}}$):**
  Average reward over valid task decisions, excluding inactive steps:
  $$\text{Utility}_{\text{active}} = \frac{\sum_{t \in T_{\mathrm{active}}} U_{\mathrm{PRR}}(t)}{|T_{\mathrm{active}}|}$$
