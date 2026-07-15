# N8_REPRODUCTION_REPORT.md

This document compares the $N=8$ fleet evaluation outputs under both baseline and corrected environments against the manuscript utility targets.

---

## 1. Metric Evaluation Table (Baseline Recreation)

| Policy Type | Metric Denominator | System Utility ($U_{\mathrm{PRR}}$) | Paper Target | Absolute Error | Relative Error | Status (5%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| MA-ROPE | active_task | 0.9618 | 0.8443 | 0.1175 | 13.92% | **WARNING** |
| ALLOFFLOAD | active_task | 0.6651 | 0.8166 | 0.1515 | 18.55% | **WARNING** |

---

## 2. Decomposed Simulator Outputs (N=8 physically_corrected)

| Policy Type | System Utility | Empirical PRR | fleet OTR | Latency (ms) | Energy (Step) | Energy (Active) | Queue Loss |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| MA-ROPE | 0.9097 | 98.4% | 84.8% | 105.6 | 0.2143 J | 0.2123 J | 0.0159 |
| ALLOFFLOAD | 0.8104 | 93.0% | 32.6% | 228.9 | 0.4572 J | 0.4588 J | 0.0696 |
| NOOFFLOAD | 0.8554 | 100.0% | 100.0% | 240.6 | 0.4854 J | 0.4811 J | 0.0000 |
