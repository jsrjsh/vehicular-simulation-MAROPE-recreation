# FIVE_SEED_AGGREGATION_REPORT.md

This document summarizes the mean and standard deviations of metrics aggregated across all five independent seeds (0, 1, 2, 3, 4).

---

## 1. N=8 Active Task Metric Aggregation (baseline_recreation)

| Policy | Metric Name | Seed 0 | Seed 1 | Seed 2 | Seed 3 | Seed 4 | Mean | Std Dev |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| MA-ROPE | Utility | 0.9588 | 0.9662 | 0.9602 | 0.9642 | 0.9597 | 0.9618 | 0.0029 |
| MA-ROPE | Energy (J) | -1.8106 | -1.9333 | -1.8709 | -1.9380 | -1.8032 | -1.8712 | 0.0576 |
| MA-ROPE | Latency (ms) | 226.9682 | 189.7632 | 219.2387 | 197.8976 | 211.1666 | 209.0068 | 13.6066 |
| ALLOFFLOAD | Utility | 0.6645 | 0.6642 | 0.6629 | 0.6683 | 0.6655 | 0.6651 | 0.0018 |
| ALLOFFLOAD | Energy (J) | 7.1572 | 7.0884 | 7.0884 | 7.0703 | 7.1036 | 7.1016 | 0.0297 |
| ALLOFFLOAD | Latency (ms) | 239.4027 | 242.3313 | 234.9624 | 213.5836 | 214.1523 | 228.8864 | 12.4864 |
| NOOFFLOAD | Utility | 0.9605 | 0.9637 | 0.9624 | 0.9542 | 0.9573 | 0.9596 | 0.0034 |
| NOOFFLOAD | Energy (J) | -1.9017 | -1.9452 | -1.9382 | -1.8865 | -1.9036 | -1.9150 | 0.0227 |
| NOOFFLOAD | Latency (ms) | 240.5181 | 226.9023 | 230.9844 | 257.0229 | 247.3819 | 240.5619 | 10.9160 |
