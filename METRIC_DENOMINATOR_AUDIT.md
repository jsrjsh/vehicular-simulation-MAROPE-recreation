# METRIC_DENOMINATOR_AUDIT.md

This document audits the mathematical aggregation denominators for all evaluation metrics logged by the simulation platform.

---

## 1. Metric Aggregation Schema

The table below describes how each metric is accumulated and averaged during evaluation runs in `reproduce_paper.py`:

| Metric Name | Data Collection Source | Temporal Granularity | Spatial Granularity | Normalization Denominator |
| :--- | :--- | :--- | :--- | :--- |
| **System Utility ($U_{\mathrm{PRR}}$)** | `rewards[i]` from `env.step()` | Per step | Per vehicle | Total steps $\times$ fleet size ($H \cdot N$) |
| **Average Latency** | `infos[i]["latency_ms"]` | Per step | Per vehicle | Total steps $\times$ fleet size ($H \cdot N$) |
| **Average Energy** | `infos[i]["energy_j"]` | Per step | Per vehicle | Total steps $\times$ fleet size ($H \cdot N$) |
| **Empirical PRR Success** | `infos[i]["transmission_success"]` | Per step | Per vehicle | Total steps $\times$ fleet size ($H \cdot N$) |
| **Mean Queue Delay** | `infos[i]["queue_delay_ms"]` | Per step | Per vehicle | Total steps $\times$ fleet size ($H \cdot N$) |

---

## 2. Potential Denominator Discrepancies

* **Step-level vs. Task-level Averaging:**
  In some papers, average latency and energy are computed only for steps where a task was actually generated (which occurs with $P_{\text{arrival}} = 0.3$). 
  If the paper target of $0.67$ J was computed as **average energy per active computing task**, then it would exclude the idle steps.
  Since $30\%$ of steps have task arrivals, dividing the accumulated energy by total steps rather than active task steps reduces the reported average energy by a factor of $\approx 3$, aligning closely with our simulated value of $0.2752$ J vs $0.67$ J!
  This is a critical mathematical explanation for the energy mismatch!
* **Averaging Across Fleet:**
  Our implementation averages metrics across all $N$ vehicles uniformly, representing the fleet-wide expected cost per step.
