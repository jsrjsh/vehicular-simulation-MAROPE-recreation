# N32_REPRODUCTION_REPORT.md

This document compares the $N=32$ fleet evaluation outputs under `baseline_recreation` against exact manuscript values.

---

## 1. Paper Reproduction Table (Baseline Recreation)

| Policy | Metric Name | Target Value | Simulated Mean | Std Dev | Abs Error | Rel Error | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| MA-ROPE | U_PRR | 0.8323 | 0.9576 | 0.0019 | 0.1253 | 15.05% | **FAIL** |
| MA-ROPE | U_OTR | 0.7424 | 0.9569 | 0.0024 | 0.2145 | 28.89% | **FAIL** |
| MA-ROPE | Fleet OTR | 0.8340 | 0.8894 | 0.0140 | 0.0554 | 6.64% | **WARNING** |
| MA-ROPE | Energy | 0.7057 | -1.8108 | 0.0269 | 2.5165 | 356.59% | **FAIL** |
| MA-ROPE | Latency | 213.0000 | 223.4476 | 5.3518 | 10.4476 | 4.90% | **PASS** |
| ALLOFFLOAD | U_PRR | 0.7790 | 0.6076 | 0.0009 | 0.1714 | 22.00% | **FAIL** |
| ALLOFFLOAD | U_OTR | 0.5644 | 0.1264 | 0.0058 | 0.4380 | 77.60% | **FAIL** |
| ALLOFFLOAD | Fleet OTR | 0.5250 | 0.1246 | 0.0073 | 0.4004 | 76.26% | **FAIL** |
| ALLOFFLOAD | Energy | 0.9441 | 7.1036 | 0.0095 | 6.1595 | 652.42% | **FAIL** |
| ALLOFFLOAD | Latency | 176.9000 | 829.9795 | 2.2051 | 653.0795 | 369.18% | **FAIL** |
| NOOFFLOAD | U_PRR | 0.8442 | 0.9610 | 0.0008 | 0.1168 | 13.84% | **FAIL** |
| NOOFFLOAD | U_OTR | 0.2754 | 0.9614 | 0.0007 | 0.6860 | 249.09% | **FAIL** |
| NOOFFLOAD | Fleet OTR | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 0.00% | **PASS** |
| NOOFFLOAD | Energy | 0.5032 | -1.9411 | 0.0133 | 2.4443 | 485.75% | **FAIL** |
| NOOFFLOAD | Latency | 248.1000 | 233.6699 | 3.5549 | 14.4301 | 5.82% | **WARNING** |
