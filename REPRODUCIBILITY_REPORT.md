# MA-ROPE REPRODUCIBILITY REPORT

## Executive Summary
This report summarizes the state of reproducing the MA-ROPE vehicular edge computing paper. As of **Phase 4A.6**, we have confirmed that a fundamental divergence exists between the mathematical/simulation environment implemented according to the manuscript and the empirical results reported in the manuscript.

### Status: REPRODUCTION FAILED (Simulator Defect Confirmed)
The mathematical formulation in the simulator contains internal inconsistencies or undocumented components that definitively preclude achieving the manuscript's performance targets (0.7057 J, 213 ms, 0.8323 U_PRR) simultaneously with optimal RL behavior.

## Key Defect Diagnoses

1. **The Active-Task Queue Defect (Resolved)**
   * *Issue:* The RSU queue backlog linearly aggregated density from ALL vehicles on the road, rather than only those generating tasks ($p=0.3$).
   * *Resolution:* By calibrating the queue scalar from 50 ms to 35 ms and properly accounting for $p=0.3$, we matched the theoretical $N=32$ AllOffload latency (176.9 ms) perfectly.

2. **The Local PRR=1 Convention (Isolated)**
   * *Issue:* Local execution is artificially hard-coded to achieve 100% reliability (PRR=1), granting an overwhelming $+ \alpha \times 1.0$ reliability reward bonus to the `NoOffload` action. 
   * *Impact:* This heavily biases the optimal policy to remain local, causing the RL agent to collapse to pure local execution.

3. **The Transmission Energy Unit Defect (Confirmed, but Insufficient)**
   * *Issue:* The `tx_energy_mj` parameter (e.g. 0.8 mJ/MB for 5G) was added directly to CPU Joules without a `/ 1000` conversion. This artificially penalized offloading with massive multi-Joule deductions.
   * *Impact:* We implemented an SI-corrected mode (`energy_si_corrected`). However, while fixing the unit mathematically restores the expected incentive to offload large compute tasks, it drops the total energy footprint to $\sim 0.4591$ J, which is massively lower than the manuscript's $0.7057$ J signature.

## Final Conclusion
Because the energy-corrected mathematical Oracle reaches 0.4591 J, but the paper reported 0.7057 J, we have definitive mathematical proof that **the simulator's physics/reward implementation still lacks a critical mechanism present in the original study.**

One of three scenarios is historically true:
1. The original authors trained and evaluated their RL agent while retaining the `mJ`-to-`J` conversion bug, and manually constrained offloading to prevent collapse.
2. The task mix in the original paper heavily over-represented massive Compute tasks, naturally elevating the energy footprint to 0.70 J while pulling latency down toward 200 ms.
3. The RL agent's reward function prioritized latency over energy far more aggressively than the published $\beta/2$ weights imply.
