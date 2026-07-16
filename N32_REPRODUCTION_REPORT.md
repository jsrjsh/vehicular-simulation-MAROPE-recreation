# N32_REPRODUCTION_REPORT.md

This document compares the $N=32$ fleet evaluation outputs under `baseline_recreation` against exact manuscript values.

---

## 1. Paper Reproduction Table (Baseline Recreation)

| Policy | Metric Name | Target Value | Simulated Mean | Std Dev | Abs Error | Rel Error | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| MA-ROPE | U_PRR | 0.8323 | 0.9571 | 0.0015 | 0.1248 | 15.00% | **FAIL** |
| MA-ROPE | U_OTR | 0.7424 | 0.5241 | 0.0029 | 0.2183 | 29.40% | **FAIL** |
| MA-ROPE | Fleet OTR | 0.8340 | 0.8882 | 0.0133 | 0.0542 | 6.50% | **WARNING** |
| MA-ROPE | Energy | 0.7057 | -1.8090 | 0.0266 | 2.5147 | 356.34% | **FAIL** |
| MA-ROPE | Latency | 213.0000 | 222.9288 | 6.4111 | 9.9288 | 4.66% | **PASS** |
| ALLOFFLOAD | U_PRR | 0.7790 | 0.6076 | 0.0009 | 0.1714 | 22.00% | **FAIL** |
| ALLOFFLOAD | U_OTR | 0.5644 | 0.1264 | 0.0058 | 0.4380 | 77.60% | **FAIL** |
| ALLOFFLOAD | Fleet OTR | 0.5250 | 0.1246 | 0.0073 | 0.4004 | 76.26% | **FAIL** |
| ALLOFFLOAD | Energy | 0.9441 | 7.1036 | 0.0095 | 6.1595 | 652.42% | **FAIL** |
| ALLOFFLOAD | Latency | 176.9000 | 829.9795 | 2.2051 | 653.0795 | 369.18% | **FAIL** |
| NOOFFLOAD | U_PRR | 0.8442 | 0.9610 | 0.0008 | 0.1168 | 13.84% | **FAIL** |
| NOOFFLOAD | U_OTR | 0.2754 | 0.5079 | 0.0016 | 0.2325 | 84.43% | **FAIL** |
| NOOFFLOAD | Fleet OTR | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 0.00% | **PASS** |
| NOOFFLOAD | Energy | 0.5032 | -1.9411 | 0.0133 | 2.4443 | 485.75% | **FAIL** |
| NOOFFLOAD | Latency | 248.1000 | 233.6699 | 3.5549 | 14.4301 | 5.82% | **WARNING** |
