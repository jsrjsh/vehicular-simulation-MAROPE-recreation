# EXECUTION_REPORT.md

Diagnostic ID: `CAMPAIGN_TRAINING_DURATION_20260803`
Purpose: Determine whether MA-ROPE's WiFi6 over-reliance (identified in QUEUE_LOSS_ROOT_CAUSE_REPORT.md) is a converged policy tradeoff or an artifact of the standard 100-episode training protocol not having converged.

## Raw trajectory (data only, no interpretation)

| Episodes trained | Checkpoint hash | conditional_tx_failure_rate | fleet_tx_failure_rate | Fleet OTR | Energy (active) | Latency (active) | RAT usage (0=Local,1=LTE,2=ITS-G5,3=WiFi6,4=5G-NR) |
|---|---|---|---|---|---|---|---|
| 100 | `c819e7a3` | 0.0591 | 0.0026 | 0.9056 | -1.8022 | 224.58 | {'0': 15280, '1': 85, '2': 181, '3': 186, '4': 268} |
| 100 | `92913fdb` | 0.0474 | 0.0022 | 0.9001 | -1.8309 | 213.10 | {'0': 15282, '1': 84, '2': 185, '3': 180, '4': 269} |
| 100 | `d35be54c` | 0.0657 | 0.0029 | 0.8662 | -1.8129 | 220.30 | {'0': 15302, '1': 74, '2': 185, '3': 185, '4': 254} |
| 250 | `dc1196ba` | 0.0603 | 0.0026 | 0.9032 | -1.7956 | 221.98 | {'0': 15286, '1': 89, '2': 187, '3': 171, '4': 267} |
| 250 | `af736d2a` | 0.0523 | 0.0023 | 0.8909 | -1.8437 | 218.71 | {'0': 15310, '1': 71, '2': 168, '3': 178, '4': 273} |
| 250 | `c2e9fafe` | 0.0569 | 0.0026 | 0.8972 | -1.8498 | 209.90 | {'0': 15302, '1': 69, '2': 197, '3': 175, '4': 257} |
| 500 | `b216fd57` | 0.0592 | 0.0026 | 0.8835 | -1.8191 | 226.94 | {'0': 15300, '1': 80, '2': 162, '3': 185, '4': 273} |
| 500 | `96ebf62d` | 0.0651 | 0.0028 | 0.8969 | -1.8133 | 222.91 | {'0': 15299, '1': 69, '2': 169, '3': 187, '4': 276} |
| 500 | `31e214e1` | 0.0633 | 0.0028 | 0.8818 | -1.7774 | 236.83 | {'0': 15291, '1': 75, '2': 176, '3': 175, '4': 283} |
