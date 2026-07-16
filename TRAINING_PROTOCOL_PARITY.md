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
| baseline_recreation | 8 | 0 | b2eccd50 | 10000 | 200 | 120s |
| baseline_recreation | 8 | 1 | e0988039 | 10000 | 200 | 120s |
| baseline_recreation | 8 | 2 | 09f1a0ab | 10000 | 200 | 120s |
| baseline_recreation | 8 | 3 | cee74fe0 | 10000 | 200 | 120s |
| baseline_recreation | 8 | 4 | e461b0dd | 10000 | 200 | 120s |
| physically_corrected | 8 | 0 | 381ca8e3 | 10000 | 200 | 120s |
| physically_corrected | 8 | 1 | 1c15e90f | 10000 | 200 | 120s |
| physically_corrected | 8 | 2 | aa032941 | 10000 | 200 | 120s |
| physically_corrected | 8 | 3 | 61f64d8f | 10000 | 200 | 120s |
| physically_corrected | 8 | 4 | c84f9cb6 | 10000 | 200 | 120s |
| baseline_recreation | 32 | 0 | 63085fc4 | 10000 | 200 | 120s |
| baseline_recreation | 32 | 1 | bc43e5da | 10000 | 200 | 120s |
| baseline_recreation | 32 | 2 | 631ef26a | 10000 | 200 | 120s |
| baseline_recreation | 32 | 3 | 1aad8e77 | 10000 | 200 | 120s |
| baseline_recreation | 32 | 4 | a7523341 | 10000 | 200 | 120s |
| physically_corrected | 32 | 0 | 67939f68 | 10000 | 200 | 120s |
| physically_corrected | 32 | 1 | 67f14bac | 10000 | 200 | 120s |
| physically_corrected | 32 | 2 | 6bcfb9ce | 10000 | 200 | 120s |
| physically_corrected | 32 | 3 | 4a6b69b9 | 10000 | 200 | 120s |
| physically_corrected | 32 | 4 | f1f94e74 | 10000 | 200 | 120s |
