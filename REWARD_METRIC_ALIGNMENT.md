# REWARD METRIC ALIGNMENT

This document audits whether the agent's internal training reward (used for Q-learning) perfectly matches the externally reported performance metric ($U_{\mathrm{PRR}}$).

## 1. Metric Alignment by Action Type

The system evaluates Utility using Eq. 4a:
$U = \alpha \cdot \text{Reliability} + \frac{\beta}{2} e^{-L/D} + \frac{\beta}{2} e^{-E/3} + \frac{\beta}{4} \Delta\text{CBR}$

| Action Type | Reliability in Training Reward | Reliability in Reported $U_{\mathrm{PRR}}$ | Reliability in Reported $U_{\mathrm{OTR}}$ | Mathematical Alignment |
| :--- | :--- | :--- | :--- | :--- |
| **Local** (`rho=0`) | $1.0$ (Hardcoded) | $1.0$ (Hardcoded) | $0.0$ (since no transmissions) | **IDENTICAL** (Reward = $U_{\mathrm{PRR}}$) |
| **Partial Offload** | Empirical PRR ($n_{rx}/n_{tx}$) | Empirical PRR ($n_{rx}/n_{tx}$) | Fleet OTR | **IDENTICAL** (Reward = $U_{\mathrm{PRR}}$) |
| **Full Offload** | Empirical PRR ($n_{rx}/n_{tx}$) | Empirical PRR ($n_{rx}/n_{tx}$) | Fleet OTR | **IDENTICAL** (Reward = $U_{\mathrm{PRR}}$) |

## 2. Term-by-Term Consistency Check

1. **Reliability Term:** The training loop captures `rewards_dict[i]` which uses empirical PRR in the `environment.step()` function. The evaluation loop simply averages these exact step rewards and reports them as `u_prr`. Therefore, the reliability term is identical.
2. **Latency Term:** The factor $\frac{\beta}{2} e^{-L/D}$ is evaluated identically.
3. **Energy Term:** The factor $\frac{\beta}{2} e^{-E/3}$ is evaluated identically.
4. **Congestion Term:** The factor $\frac{\beta}{4} \Delta\text{CBR}$ is evaluated identically.

## 3. Conclusion
The training reward and the reported $U_{\mathrm{PRR}}$ are **mathematically identical**. 
The agent is training directly on the exact objective function that is reported in the tables. 
There is no mismatch between the training objective ($U_{\mathrm{PRR}}$) and the evaluation objective ($U_{\mathrm{PRR}}$).

However, there is a fundamental split between $U_{\mathrm{PRR}}$ and $U_{\mathrm{OTR}}$:
* The training reward ($U_{\mathrm{PRR}}$) treats local execution as "100% successful" ($\text{PRR} = 1.0$).
* The evaluation metric $U_{\mathrm{OTR}}$ treats local execution as "0% on-time network delivery" ($\text{OTR} = 0.0$).
