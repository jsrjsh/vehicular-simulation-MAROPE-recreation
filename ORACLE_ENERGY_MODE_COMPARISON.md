# ORACLE ENERGY MODE COMPARISON

The following results were computed over $N=32$, 5 seeds (100 episodes each), in the `manuscript_calibrated` environment queue mode.

## 1. Legacy Unconverted Mode (mJ added to J)
| Policy | $U_{PRR}$ | Energy (J) | Latency (ms) | Safety | Infotainment | Compute |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NoOffload** | **0.8559** | 0.4777 | 238.9 | 0.9361 | 0.8359 | 0.5525 |
| **AllOffload** | 0.7789 | 0.4844 | 322.0 | 0.8297 | 0.8055 | 0.5391 |
| **TaskRuleOracle** | 0.8544 | 0.4773 | 235.5 | 0.9360 | 0.8357 | 0.5385 |
| **Greedy** | 0.8544 | 0.4773 | 235.5 | 0.9360 | 0.8357 | 0.5385 |

*Note: Greedy correctly defaults to TaskRuleOracle because the mathematical penalty of 4.0 Joules for offloading Compute prevents offloading.*

## 2. SI Corrected Mode (mJ / 1000)
| Policy | $U_{PRR}$ | Energy (J) | Latency (ms) | Safety | Infotainment | Compute |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NoOffload** | **0.8559** | 0.4777 | 238.9 | 0.9361 | 0.8359 | 0.5525 |
| **AllOffload** | 0.7797 | 0.4738 | 322.0 | 0.8297 | 0.8070 | 0.5420 |
| **TaskRuleOracle** | 0.8548 | 0.4709 | 235.5 | 0.9360 | 0.8357 | 0.5413 |
| **Greedy** | 0.8515 | **0.4591** | 229.5 | 0.9363 | 0.8075 | 0.5402 |

*Note: Under SI correction, the Greedy agent's energy footprint drops to 0.4591 Joules as it intelligently offloads tasks to edge infrastructure, but its System Utility $U_{PRR}$ still trails NoOffload (0.8515 vs 0.8559).*
