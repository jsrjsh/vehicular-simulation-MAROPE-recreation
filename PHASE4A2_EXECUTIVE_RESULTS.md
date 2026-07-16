# PHASE4A2_EXECUTIVE_RESULTS.md

## Required N=8 Table

| Baseline Method / Metric | Paper Target Value | Simulator Value (Physically Corrected) | Absolute Error | Relative Error | Pass / Fail (Threshold 5%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **MA-ROPE Utility** | 0.8400 | 0.8547 | 0.0147 | 1.75% | **PASS** |
| **MA-ROPE Energy** | 0.6700 | 0.4760 | 0.1940 | 28.96% | **WARNING** |
| **AllOffload Utility** | 0.8200 | 0.7818 | 0.0382 | 4.66% | **PASS** |
| **AllOffload Energy** | 0.9000 | 0.8982 | 0.0018 | 0.20% | **PASS** |
| **NoOffload Utility** | - | 0.8614 | - | - | - |
| **NoOffload Energy** | - | 0.4488 | - | - | - |

---

## Required N=32 Table (Physically Corrected, 5 seeds, 100 episodes)

| Policy | Metric Name | Target Value | Simulated Mean | Std Dev | Abs Error | Rel Error | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **MA-ROPE** | U_PRR | 0.8323 | 0.8659 | 0.0152 | 0.0336 | 4.03% | **PASS** |
| **MA-ROPE** | U_OTR | 0.7424 | 0.6864 | 0.2570 | 0.0560 | 7.54% | **WARNING** |
| **MA-ROPE** | Fleet OTR | 0.8340 | 0.7657 | 0.0322 | 0.0683 | 8.19% | **WARNING** |
| **MA-ROPE** | Energy (J) | 0.7057 | 0.4103 | 0.0831 | 0.2954 | 41.86% | **FAIL** |
| **MA-ROPE** | Latency (ms)| 213.0000 | 202.9571 | 40.4964 | 10.0429 | 4.71% | **PASS** |
| **ALLOFFLOAD**| U_PRR | 0.7790 | 0.7127 | 0.0089 | 0.0663 | 8.51% | **WARNING** |
| **ALLOFFLOAD**| U_OTR | 0.5644 | 0.2580 | 0.0152 | 0.3064 | 54.29% | **FAIL** |
| **ALLOFFLOAD**| Fleet OTR | 0.5250 | 0.1189 | 0.0268 | 0.4061 | 77.35% | **FAIL** |
| **ALLOFFLOAD**| Energy (J) | 0.9441 | 0.9690 | 0.0683 | 0.0249 | 2.64% | **PASS** |
| **ALLOFFLOAD**| Latency (ms)| 176.9000 | 829.9795 | 21.6958 | 653.0795 | 369.18% | **FAIL** |
| **NOOFFLOAD** | U_PRR | 0.8442 | 0.8583 | 0.0075 | 0.0141 | 1.67% | **PASS** |
| **NOOFFLOAD** | U_OTR | 0.2754 | 0.3002 | 0.0066 | 0.0248 | 9.01% | **WARNING** |
| **NOOFFLOAD** | Fleet OTR | 0.0000 | 1.0000 | 0.0000 | 1.0000 | N/A | **N/A** |
| **NOOFFLOAD** | Energy (J) | 0.5032 | 0.4673 | 0.0362 | 0.0359 | 7.13% | **WARNING** |
| **NOOFFLOAD** | Latency (ms)| 248.1000 | 233.6699 | 18.1196 | 14.4301 | 5.82% | **WARNING** |

