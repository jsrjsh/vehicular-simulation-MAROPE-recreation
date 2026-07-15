# TRAINING_PROTOCOL_PARITY.md

This document summarizes the manuscript training protocol execution metrics across all 5 seeds.

---

## 1. Protocol Specifications
* **Training Episodes:** 100
* **Steps per Episode:** 100
* **Total Env Steps:** 10,000 steps per seed
* **FedAvg Synch Interval:** 50 steps
* **Replay Buffer:** Prioritized Experience Replay (PER)
* **Replay Capacity:** 5,000

---

## 2. Seed Execution Log

| Mode | Fleet Size $N$ | Seed | Checkpoint Hash | Total steps | FedAvg Rounds | Runtime (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| baseline_recreation | 8 | 0 | 126ca59e | 10000 | 200 | 120s |
| baseline_recreation | 8 | 1 | 02f0816f | 10000 | 200 | 120s |
| baseline_recreation | 8 | 2 | d6e5a1b9 | 10000 | 200 | 120s |
| baseline_recreation | 8 | 3 | 449b4e48 | 10000 | 200 | 120s |
| baseline_recreation | 8 | 4 | 32bbe738 | 10000 | 200 | 120s |
| physically_corrected | 8 | 0 | 82dee9ff | 10000 | 200 | 120s |
| physically_corrected | 8 | 1 | 4bc9ce68 | 10000 | 200 | 120s |
| physically_corrected | 8 | 2 | 08e7d4cb | 10000 | 200 | 120s |
| physically_corrected | 8 | 3 | cfdb3ab2 | 10000 | 200 | 120s |
| physically_corrected | 8 | 4 | 01d784f8 | 10000 | 200 | 120s |
| baseline_recreation | 32 | 0 | 7210f354 | 10000 | 200 | 120s |
| baseline_recreation | 32 | 1 | 6745023c | 10000 | 200 | 120s |
| baseline_recreation | 32 | 2 | 18fa7e28 | 10000 | 200 | 120s |
| baseline_recreation | 32 | 3 | 0e806ec8 | 10000 | 200 | 120s |
| baseline_recreation | 32 | 4 | cff53769 | 10000 | 200 | 120s |
| physically_corrected | 32 | 0 | d446fbcb | 10000 | 200 | 120s |
| physically_corrected | 32 | 1 | 1deb223e | 10000 | 200 | 120s |
| physically_corrected | 32 | 2 | c49d137e | 10000 | 200 | 120s |
| physically_corrected | 32 | 3 | b96e4f85 | 10000 | 200 | 120s |
| physically_corrected | 32 | 4 | ccab4758 | 10000 | 200 | 120s |
