# MANUSCRIPT_CALIBRATED_POLICY_REPORT.md

This document verifies the training outcomes of MA-ROPE under the `manuscript_calibrated` environment.

## N=32 Results

| Policy | Metric | Target | Simulated | Status |
| :--- | :--- | :---: | :---: | :---: |
| MA-ROPE | U_PRR | 0.8323 | 0.8572 | **PASS** |
| MA-ROPE | Energy | 0.7057 | 0.4685 | **WARNING** |
| MA-ROPE | Latency | 213.0 | 229.2029 | **WARNING** |
| ALLOFFLOAD | U_PRR | 0.7790 | 0.7897 | **PASS** |
| ALLOFFLOAD | Energy | 0.9441 | 0.9690 | **PASS** |
| ALLOFFLOAD | Latency | 176.9 | 175.6748 | **PASS** |
| NOOFFLOAD | U_PRR | 0.8442 | 0.8583 | **PASS** |
| NOOFFLOAD | Energy | 0.5032 | 0.4673 | **WARNING** |
| NOOFFLOAD | Latency | 248.1 | 233.6699 | **WARNING** |
