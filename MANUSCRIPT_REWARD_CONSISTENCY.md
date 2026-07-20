# MANUSCRIPT REWARD CONSISTENCY

This document audits four simultaneous claims implied or stated in the manuscript and recreation guide to determine their logical consistency.

## 1. The Four Claims
1. **PRR defined only for transmitted PDUs:** The text and equations define PRR as $n_{rx} / n_{tx}$. For local execution, $n_{tx} = 0$, rendering the formula $0/0$.
2. **NoOffload $U_{\mathrm{PRR}}$ = 0.8442:** The manuscript reports the deterministic NoOffload policy achieving a System Utility ($U_{\mathrm{PRR}}$) of 0.8442 (at N=32).
3. **NoOffload Fleet OTR = 0:** The evaluation tables show that the On-Time Ratio (OTR) for NoOffload is zero, since no packets are transmitted over the network.
4. **$U_{\mathrm{PRR}}$ used as training reward:** The step-level training reward optimized by the RL agent is exactly the System Utility $U_{\mathrm{PRR}}$.

## 2. Consistency Analysis

Are these statements mutually consistent? **No, not without a hidden convention.**

If PRR is strictly defined only for transmitted PDUs, then for `NoOffload` (where no transmissions occur), the PRR is either undefined ($0/0$) or $0$. 
If $\text{PRR} = 0$, the $U_{\mathrm{PRR}}$ equation ($\alpha \cdot \text{PRR} + \dots$) would drop the $\alpha$ term entirely. For a Safety task ($\alpha=0.7$), dropping the reliability term would crash the maximum possible reward to $\sim 0.23$. Averaged across the fleet, the maximum possible System Utility for NoOffload would be around $\sim 0.20$.
However, the manuscript reports NoOffload $U_{\mathrm{PRR}} = 0.8442$. This is mathematically impossible unless the $\alpha$ term is fully credited for NoOffload.

## 3. The Hidden Convention

To make all four statements mathematically consistent, the simulation MUST employ the following **undocumented convention**:

**"When a task is executed locally (NoOffload), the evaluation of PRR in the reward function is forcibly set to $1.0$ (100% reliable), but the evaluation of OTR in the network metrics is set to $0.0$ (0% network delivery)."**

By adopting this asymmetric convention:
* The training reward correctly gives $U_{\mathrm{PRR}} = 0.8442$ for NoOffload (satisfying Claim 2 and 4).
* The evaluation script yields Fleet OTR = 0 for NoOffload (satisfying Claim 3).
* Claim 1 (PRR defined only for tx) is technically violated in the code logic, but mathematically bypassed by the `if local: PRR=1` branch.

This hidden convention is the exact mechanism that causes the NoOffload policy to dominate the reward landscape. By granting local execution a guaranteed 100% PRR reliability score, the RL agent is heavily incentivized to avoid the unpredictable, queue-delayed wireless channel.
