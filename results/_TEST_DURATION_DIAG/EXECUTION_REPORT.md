# EXECUTION_REPORT.md

Diagnostic ID: `_TEST_DURATION_DIAG`
Purpose: Determine whether MA-ROPE's WiFi6 over-reliance (identified in QUEUE_LOSS_ROOT_CAUSE_REPORT.md) is a converged policy tradeoff or an artifact of the standard 100-episode training protocol not having converged.

## Raw trajectory (data only, no interpretation)

| Episodes trained | Checkpoint hash | conditional_tx_failure_rate | fleet_tx_failure_rate | Fleet OTR | Energy (active) | Latency (active) | RAT usage (0=Local,1=LTE,2=ITS-G5,3=WiFi6,4=5G-NR) |
|---|---|---|---|---|---|---|---|
| 1 | `13c07f33` | 0.0181 | 0.0180 | 0.9819 | -0.1634 | 36.70 | {'0': 5, '1': 4, '2': 7, '3': 8, '4': 976} |
| 2 | `84a8785b` | 0.0333 | 0.0010 | 0.9667 | -1.7985 | 220.35 | {'0': 960, '1': 4, '2': 7, '3': 8, '4': 21} |
| 3 | `a8391c2c` | 0.0251 | 0.0230 | 0.9687 | -0.0833 | 92.74 | {'0': 64, '1': 4, '2': 8, '3': 8, '4': 916} |
