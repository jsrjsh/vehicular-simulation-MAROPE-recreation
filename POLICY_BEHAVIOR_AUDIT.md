# POLICY BEHAVIOR AUDIT

This document audits the action distribution of the MA-ROPE agent after a short training run (100 episodes) in the calibrated environment.

## 1. Action Histogram
Out of 980 generated tasks during the evaluation phase, the agent selected the following actions:

* **Action 0 (Local Execution):** 617 (63.0%)
* **Action 1-4 (LTE Offloading):** 50 (5.1%)
* **Action 5-9 (ITS-G5 / Wi-Fi Offloading):** 283 (28.8%)
* **Action 10 (5G Full Offloading):** 30 (3.1%)

**Overall Fractions:**
* **Fraction Local:** 63.0%
* **Fraction Partial Offload:** 33.9%
* **Fraction Full Offload:** 3.1%

*(Note: During the full evaluation over many seeds where $\epsilon$ decays fully, the fraction local collapses even further toward $>90\%$, driving the energy down to 0.4685 J).*

## 2. Task-Conditioned Action Histogram

**Safety Tasks (610 total):**
* Local (Action 0): 381 (62%)
* Partial Offload: 209 (34%)
* Full Offload: 20 (3%)

**Infotainment Tasks (207 total):**
* Local (Action 0): 132 (63%)
* Partial Offload: 70 (34%)
* Full Offload: 5 (2%)

**Compute Tasks (163 total):**
* Local (Action 0): 104 (63%)
* Partial Offload: 54 (33%)
* Full Offload: 5 (3%)

## 3. Reward and Energy Contribution by Task Type

| Task Type | Average Step Reward ($U$) | Average Energy (J) |
| :--- | :--- | :--- |
| **Safety** | 0.8329 | 0.5480 |
| **Infotainment** | 0.8204 | 0.6237 |
| **Compute** | 0.8400 | 0.4891 |

## 4. Conclusion
The agent completely ignores the physics of the different task types. Rather than specializing (e.g., executing Safety locally and offloading Compute), the agent adopts a nearly uniform strategy across all task types: **Choose Local Execution (~63% of the time)**. 
When it does explore, it prefers partial offloading over short-range ITS-G5 (Action 5) rather than 5G (Action 10), likely due to lower queue contention. 

The policy has collapsed into a safe, local-dominant minimum.
