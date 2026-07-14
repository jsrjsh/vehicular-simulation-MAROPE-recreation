# PAPER_VS_RECREATION_CONFIG.md

This document compares the simulation parameters of the manuscript against our recreation setup.

---

## 1. Parity Table

| Config Field | Manuscript / Spec Value | Recreation Value | Status | Analysis / Notes |
| :--- | :--- | :--- | :---: | :--- |
| **Environment Mode** | Dual-mode supported | Both supported | **MATCH** | Evaluated under both modes in Phase 4A.1. |
| **N Vehicles** | 8 | 8 | **MATCH** | Used in paper reproduction runner. |
| **R RSUs** | 2 | 2 | **MATCH** | Placed at 500 m and 1500 m. |
| **Road Length/Topology** | 2600 m toroidal | 2600 m toroidal | **MATCH** | Wraps around correctly. |
| **Speed Distribution** | $U(20, 38)$ m/s | $U(20, 38)$ m/s | **MATCH** | Kinematics match. |
| **Task Mix** | URLLC [0.65, 0.20, 0.15] | Same | **MATCH** | Task selection match. |
| **Task Sizes** | 0.1 MB, 2.0 MB, 5.0 MB | Same | **MATCH** | Workloads match. |
| **CPU-cycle Demand** | 1e8, 5e8, 2e9 cycles | Same | **MATCH** | Computing workload match. |
| **Deadlines** | 100 ms, 500 ms, 1000 ms | Same | **MATCH** | Bounded correctly. |
| **ECU Frequency** | 2.0 GHz | 2.0 GHz | **MATCH** | CPU_FREQ_HZ. |
| **MEC Frequency** | remote speedup 1.5, base 0.5e-3 | Same | **MATCH** | MEC capabilities match. |
| **Queue Service Rate** | 50.0 ms | 50.0 ms | **MATCH** | DELAY_PER_UNIT_MS. |
| **Queue Saturation Rule** | $Q_r = \sum \rho_i$ | Same | **MATCH** | Aggregated RSU queue size. |
| **RAT Latencies** | LTE 20ms, ITS 10ms, WiFi 5ms, 5G 1ms | Same | **MATCH** | Table specifications match. |
| **Transmit Power** | LTE/ITS/5G 23dBm, WiFi 20dBm | Same | **MATCH** | Power values match. |
| **Energy Coefficients** | LTE 1.5mJ, ITS 2.0mJ, WiFi 1.0mJ, 5G 0.8mJ | Same | **MATCH** | tx_energy_mj values match. |
| **Partial-offload Ratios** | 0.25, 0.50, 0.75, 1.00 | Same | **MATCH** | Adapted offload values. |
| **Action Map** | 11 discrete actions | Same | **MATCH** | Map coordinates match. |
| **Reward Weights** | safety 0.7/0.3, info 0.4/0.6, compute 0.2/0.8 | Same | **MATCH** | Rewards scale correctly. |
| **Episode Count** | 100 train / 5 eval | 30 train / 5 eval | **MISMATCH** | Runner uses 30 episodes for smoke training speed instead of 100. |
| **Steps per Episode** | 200 | 100 | **MISMATCH** | Guide specifies 200 steps (max_steps), but reproduction runner runs 100 steps. |
| **Replay Mode** | Prioritized | Prioritized | **MATCH** | PER buffer active. |
| **Replay Capacity** | 10,000 | 5,000 | **MISMATCH** | D3QN parameter provenance uses 10,000 capacity, simulator default uses 5,000. |
| **PER alpha/beta** | alpha=0.6, beta: $0.4 \to 1.0$ | Same | **MATCH** | Prioritization schedules match. |
| **Learning Rate** | 1e-3 | 1e-3 | **MATCH** | Optimizer learning rate matches. |
| **Gamma** | 0.95 | 0.95 | **MATCH** | Discount factor matches. |
| **Epsilon Schedule** | decay steps 2000 | decay steps 2000 | **MATCH** | Exploration schedule matches. |
| **Target Update Interval** | 100 steps | 100 steps | **MATCH** | Network updates match. |
| **FedAvg Interval** | 50 steps | 20 steps | **MISMATCH** | Recreation guide lists CoopEC round every 50 steps, but training script aggregated every 20 steps. |
| **Participation Threshold** | 70% | 70% | **MATCH** | Dropout aggregations match. |
| **Random Seeds** | 42 | 42 | **MATCH** | Deterministic start match. |
| **Evaluation Exploration** | epsilon = 0.05 | epsilon = 0.05 | **MATCH** | Evaluation is greedy with 0.05 noise. |
| **Metric Aggregation** | Average across fleet and episodes | Same | **MATCH** | Accumulations match. |
