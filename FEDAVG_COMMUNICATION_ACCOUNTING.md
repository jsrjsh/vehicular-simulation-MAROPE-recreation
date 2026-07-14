# FEDAVG_COMMUNICATION_ACCOUNTING.md

This document presents the communication accounting metrics tracked during synchronous multi-agent federated learning runs.

---

## 1. Static Parameter Footprint

* **Q-Network Parameter Count:** 104,139 floats
* **Serialized Model size:** 419,840 bytes (~410.0 KB)
* **Single Participant Upload footprint:** 419,840 bytes (~410.0 KB)
* **Single Participant Broadcast download footprint:** 419,840 bytes (~410.0 KB)

---

## 2. Dynamic Round-by-Round Communication Metrics

The table below logs the data transfer footprints for a 4-client federated training run (`n_agents=4`, `sync_interval=20`, `participation_prob=0.9`, 5 episodes).

| Round | Active Clients | Upload Bytes | Broadcast Bytes | Total Round Bytes | Cumulative Bytes | Round Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Round 1** | 3 | 1,259,520 | 1,679,360 | 2,938,880 (~2.80 MB) | 2,938,880 | **SUCCESS** |
| **Round 2** | 4 | 1,679,360 | 1,679,360 | 3,358,720 (~3.20 MB) | 6,297,600 | **SUCCESS** |
| **Round 3** | 3 | 1,259,520 | 1,679,360 | 2,938,880 (~2.80 MB) | 9,236,480 | **SUCCESS** |
| **Round 4** | 4 | 1,679,360 | 1,679,360 | 3,358,720 (~3.20 MB) | 12,595,200 | **SUCCESS** |
| **Round 5** | 4 | 1,679,360 | 1,679,360 | 3,358,720 (~3.20 MB) | 15,953,920 | **SUCCESS** |
| **Round 6** | 4 | 1,679,360 | 1,679,360 | 3,358,720 (~3.20 MB) | 19,312,640 | **SUCCESS** |
| **Round 7** | 4 | 1,679,360 | 1,679,360 | 3,358,720 (~3.20 MB) | 22,671,360 | **SUCCESS** |
| **Round 8** | 4 | 1,679,360 | 1,679,360 | 3,358,720 (~3.20 MB) | 26,030,080 | **SUCCESS** |
| **Round 9** | 2 | 0 | 0 | 0 | 26,030,080 | **ABORTED** (<70%) |
| **Round 10**| 4 | 1,679,360 | 1,679,360 | 3,358,720 (~3.20 MB) | 29,388,800 | **SUCCESS** |

---

## 3. Communication Scaling Projections ($N = 32$ clients)

Using these baseline values, a full-scale paper run containing $N = 32$ clients can be projected:

* **Success round footprint (100% participation):**
  * Uploads: $32 \times 410.0$ KB = 13.12 MB
  * Broadcasts: $32 \times 410.0$ KB = 13.12 MB
  * **Total round footprint:** 26.24 MB
* **Projected total data transfer for 50 episodes (250 sync rounds):**
  * $250 \times 26.24$ MB $\approx$ **6.56 GB** of network traffic.
