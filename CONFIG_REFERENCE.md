# CONFIG_REFERENCE.md

This document serves as the single-source-of-truth reference for all simulation constants, configurations, and structures implemented in [`env/config.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/env/config.py).

---

## 1. Global Simulation Parameters

| Constant | Value | Description |
| :--- | :--- | :--- |
| `CPU_FREQ_HZ` | `2e9` (2.0 GHz) | Base clock frequency of the vehicle's onboard processing unit. |
| `P_CPU_W` | `2.0` (2.0 W) | Electrical power consumed by the vehicle's CPU when computing. |
| `SAFETY_REMOTE_MEC_SPEEDUP` | `1.5` | Processing speedup multiplier at the MEC server for safety-critical tasks. |
| `remote_factor_base` | `0.5e-3` (s/MB) | Computing workload processing time coefficient on the MEC server. |
| `DELAY_PER_UNIT_MS` | `50.0` (ms) | Scaling factor translating RSU queue size $Q$ to queuing delay ($L_{\text{queue}} = Q \times 50$ ms). |
| `OBS_DIM` | `12` | Total dimensions of the state representation vector. |

---

## 2. Multi-RAT Physical and Sidelink Characteristics

The simulator models five communication interfaces (0: Local compute, 1: LTE, 2: ITS-G5, 3: WiFi-6, 4: 5G-NR):

| Parameter | Local (0) | LTE (1) | ITS-G5 (2) | WiFi-6 (3) | 5G-NR (4) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RAT Latency ($L_{\text{prop}}$)** | 0.0 ms | 20.0 ms | 10.0 ms | 5.0 ms | 1.0 ms |
| **Sidelink Bandwidth** | — | — | — | — | — |
| **Protocol Overhead (cycles)** | 1e9 | 50.0 | 27.0 | 600.0 | 1000.0 |
| **Tx Energy Per PDU** | 0.0 mJ | 1.5 mJ | 2.0 mJ | 1.0 mJ | 0.8 mJ |
| **Noise Floor ($N_0$)** | — | −110.0 dBm | −90.0 dBm | −90.0 dBm | −110.0 dBm |
| **Shadowing Deviation ($\sigma_h$)** | — | 4.0 dB | 4.0 dB | 3.0 dB | 4.0 dB |
| **SINR Threshold ($\tau$)** | — | 4.0 dB | 4.0 dB | 5.0 dB | 4.0 dB |
| **Fading Channel Profile** | none | jakes | constant | constant | jakes |
| **Carrier Frequency ($f$)** | — | 1.8 GHz | 5.9 GHz | 5.0 GHz | 3.5 GHz |
| **Transmit Power ($P_{\text{tx}}$)** | — | 23.0 dBm | 23.0 dBm | 20.0 dBm | 23.0 dBm |
| **Path Loss Formula** | none | 3gpp_v2x | 3gpp_v2x | wifi_ax | 5g_umi |

---

## 3. Action Mapping Matrix

The agent chooses from 11 discrete action indices ($a \in [0, 10]$), which map to a target RAT index and offloading ratio $\rho$:

| Action Index | Chosen RAT Index | Offloading Ratio $\rho$ | Intent / Meaning |
| :--- | :---: | :---: | :--- |
| **0** | 0 (Local) | 0.00 | Pure Local Processing |
| **1** | 1 (LTE) | 0.25 | LTE Offload 25% |
| **2** | 1 (LTE) | 0.50 | LTE Offload 50% |
| **3** | 1 (LTE) | 0.75 | LTE Offload 75% |
| **4** | 2 (ITS-G5) | 0.25 | ITS-G5 Offload 25% |
| **5** | 2 (ITS-G5) | 0.50 | ITS-G5 Offload 50% |
| **6** | 4 (5G-NR) | 0.25 | 5G Offload 25% |
| **7** | 4 (5G-NR) | 0.50 | 5G Offload 50% |
| **8** | 4 (5G-NR) | 1.00 | 5G Offload 100% (AllOffload) |
| **9** | 3 (WiFi-6) | 0.50 | WiFi Offload 50% |
| **10** | 3 (WiFi-6) | 1.00 | WiFi Offload 100% |

*Note: LTE 100% offload is not permitted. In policy, safety tasks mask actions $\{1, 2, 3\}$.*

---

## 4. Task Characteristics

| Task Profile | Deadline ($D$) | Data size ($data$) | Compute Demand ($C$) | Weight $\alpha$ (PRR) | Weight $\beta$ (Delay/Energy) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Safety** | 100 ms | 0.1 MB | $1 \times 10^8$ cycles | 0.70 | 0.30 |
| **Infotainment** | 500 ms | 2.0 MB | $5 \times 10^8$ cycles | 0.40 | 0.60 |
| **Compute-Heavy** | 1000 ms | 5.0 MB | $2 \times 10^9$ cycles | 0.20 | 0.80 |

---

## 5. Scenario Mixes

The probability distribution of generating safety, infotainment, and compute tasks per scenario:

* **URLLC Stress (`urllc`):** $P(\text{safety}) = 0.65$, $P(\text{infotainment}) = 0.20$, $P(\text{compute}) = 0.15$
* **Balanced Load (`balanced`):** $P(\text{safety}) = 0.33$, $P(\text{infotainment}) = 0.33$, $P(\text{compute}) = 0.34$
* **Compute Heavy (`compute`):** $P(\text{safety}) = 0.10$, $P(\text{infotainment}) = 0.30$, $P(\text{compute}) = 0.60$

---

## 6. Default Env Parameters

* **Road Kinematics:** Toroidal circular ring, $L = 2600.0$ m.
* **RSU Placements:** Located at coordinates $500.0$ m and $1500.0$ m.
* **Init Kinematics:** $x \sim U(8, 2600)$ m, $v \sim U(20, 38)$ m/s, $battery \sim U(70, 100)\%$.
* **Task Resampling Probability:** 0.3 at each simulation step (100 ms interval).
* **Max Episode Steps:** 200 steps (equivalent to 20 seconds of real-time simulation).
