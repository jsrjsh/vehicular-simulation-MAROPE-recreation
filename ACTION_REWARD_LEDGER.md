# ACTION REWARD LEDGER

This document hand-calculates the exact step reward ($U$) for the three task types under three different policies, using N=32 simulator state values (with `manuscript_calibrated` queue delay scalar of 35ms).

* **Reward Formula:** $U = \alpha \cdot \text{PRR} + \frac{\beta}{2} e^{-L/D} + \frac{\beta}{2} e^{-E/3} + \frac{\beta}{4} \Delta\text{CBR}$
* **Assumptions:** 
  * PRR = 1.0 (local) or 0.78 (AllOffload empirical PRR at N=32)
  * $\Delta\text{CBR} \approx 0$ (steady state)

## 1. Safety Task ($\alpha=0.70, \beta=0.30, D=100\text{ ms, } \text{Data}=0.1\text{ MB, } C=10^8$)

| Action | Latency ($L$) | Energy ($E$) | $e^{-L/D}$ | $e^{-E/3}$ | Reliability ($\alpha \cdot PRR$) | Total Reward ($U$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NoOffload** | $50.0$ ms | $0.100$ J | $0.606$ | $0.967$ | $0.700$ (PRR=1) | **$0.936$** |
| **LTE 50% (Partial)** | ~ $150$ ms | $\approx 0.05$ J | $0.223$ | $0.983$ | $\approx 0.546$ (PRR=0.78) | **$0.727$** |
| **5G 100% (All)** | $176.4$ ms | $0.000$ J | $0.171$ | $1.000$ | $0.546$ (PRR=0.78) | **$0.721$** |

**Winner for Safety:** `NoOffload` by a massive margin (+0.215), driven by the strict $100$ms deadline penalizing offload queue delays, combined with the hardcoded PRR=1 for local execution.

## 2. Infotainment Task ($\alpha=0.40, \beta=0.60, D=500\text{ ms, } \text{Data}=2.0\text{ MB, } C=5\cdot 10^8$)

| Action | Latency ($L$) | Energy ($E$) | $e^{-L/D}$ | $e^{-E/3}$ | Reliability ($\alpha \cdot PRR$) | Total Reward ($U$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NoOffload** | $250.0$ ms | $0.500$ J | $0.606$ | $0.846$ | $0.400$ (PRR=1) | **$0.835$** |
| **LTE 50% (Partial)** | ~ $160$ ms | $\approx 0.25$ J | $0.726$ | $0.920$ | $\approx 0.312$ (PRR=0.78) | **$0.805$** |
| **5G 100% (All)** | $\approx 178$ ms | $0.000$ J | $0.700$ | $1.000$ | $0.312$ (PRR=0.78) | **$0.822$** |

**Winner for Infotainment:** `NoOffload` by a tiny margin (+0.013). The energy savings of 5G offloading (+0.154 reward) are slightly outweighed by the loss of the guaranteed PRR=1 local reliability penalty (-0.088 reward) and minor latency differences.

## 3. Compute Task ($\alpha=0.20, \beta=0.80, D=1000\text{ ms, } \text{Data}=5.0\text{ MB, } C=2\cdot 10^9$)

| Action | Latency ($L$) | Energy ($E$) | $e^{-L/D}$ | $e^{-E/3}$ | Reliability ($\alpha \cdot PRR$) | Total Reward ($U$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NoOffload** | $1000.0$ ms | $2.000$ J | $0.367$ | $0.513$ | $0.200$ (PRR=1) | **$0.552$** |
| **LTE 50% (Partial)** | ~ $200$ ms | $\approx 1.00$ J | $0.818$ | $0.716$ | $\approx 0.156$ (PRR=0.78) | **$0.769$** |
| **5G 100% (All)** | $\approx 180$ ms | $0.000$ J | $0.835$ | $1.000$ | $0.156$ (PRR=0.78) | **$0.890$** |

**Winner for Compute:** `5G 100% (AllOffload)` dominates (+0.338). The massive energy consumption (2.0 J) and latency (1000 ms) of local execution make offloading strictly optimal, even with the unreliability of the wireless channel.

## Summary

The reward function creates a strongly split optimal policy:
1. **Safety:** Never offload (penalty for offloading is severe).
2. **Infotainment:** Marginally prefer no offload (nearly tied).
3. **Compute:** Always offload (penalty for local is severe).

If an agent learns this optimal policy, its expected energy use is:
$E_{avg} = 0.65(0.1) + 0.20(0.5) + 0.15(0.0) = \mathbf{0.165 \text{ J}}$

However, the retrained MA-ROPE agent achieved **0.4685 J**, implying it failed to offload even the Compute tasks, likely settling into a local minimum where `NoOffload` (Action 0) was the safest default across the board.
