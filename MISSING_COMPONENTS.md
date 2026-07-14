# MISSING_COMPONENTS.md

This document details all the missing research components that must be implemented from scratch to faithfully reconstruct the MA-ROPE simulation platform.

---

## 1. Core Simulation Environment (`env`)

### 1.1 Environment Base (`env/environment.py`)
- **Purpose/Why Needed:** Manages the simulation loop (step-by-step state transitions), vehicle initialization (position, speed, battery percentage), task generation with arrival probability $0.3$, and episode completion (200 steps). It acts as the orchestrator for all other sub-models.
- **Priority:** Critical (Blocker)
- **Dependencies:** None

### 1.2 Physical Wireless Channel Model (`env/channel.py`)
- **Purpose/Why Needed:** Computes path loss (using 3GPP V2X, 5G UMi, and WiFi 802.11ax models), shadow fading, Jakes fading (for LTE and 5G-NR), and final SINR. Computes link success probability $p$ and performs Bernoulli draws to determine transmission success.
- **Priority:** Critical
- **Dependencies:** None

### 1.3 RSU Queue Model (`env/queue.py` or within `env/environment.py`)
- **Purpose/Why Needed:** Aggregates offloading requests ($\rho$) from vehicles connected to each RSU. Computes queue backlog $Q_r$, the queuing delay proxy ($L_{\text{queue}} = Q \times 50$ ms), and the Channel Busy Ratio (CBR) proxy ($\text{CBR} = \text{clip}(Q/N, 0, 1)$).
- **Priority:** Critical
- **Dependencies:** Environment Base

### 1.4 Latency & Energy Cost Models
- **Purpose/Why Needed:** Implements the parallel-max latency formula:
  $$L_{\text{total}} = \max(L_{\text{local}}(1-\rho), L_{\text{remote}} + L_{\text{queue}} + L_{\text{offload}})$$
  And calculates the energy consumption based on CPU computation cycles and transmission power.
- **Priority:** Critical
- **Dependencies:** Environment Base, RSU Queue Model

### 1.5 12-Dimensional Observation Builder
- **Purpose/Why Needed:** Constructs the state representation vector:
  1. Normalized SINRs per RAT (4-D)
  2. Empirical Packet Reception Ratios (PRR) per RAT (4-D)
  3. Normalized RSU Queue size (1-D)
  4. Normalized task data size (1-D)
  5. Normalized task deadline (1-D)
  6. Normalized remaining battery percentage (1-D)
- **Priority:** Critical
- **Dependencies:** Environment Base, Wireless Channel Model, RSU Queue Model

### 1.6 Action Mapper & Policy Masking
- **Purpose/Why Needed:** Maps the 11 discrete actions to (RAT index, $\rho$). For safety tasks, masks actions $\{1, 2, 3\}$ (representing LTE offloading) in the policy during selection.
- **Priority:** Critical
- **Dependencies:** Environment Base

### 1.7 Reward Function ($U_{\text{PRR}}$ & $U_{\text{OTR}}$)
- **Purpose/Why Needed:** Computes the step-level training reward using Eq. 4a (based on empirical PRR, latency exponential utility, energy exponential utility, and CBR change). Also tracks the evaluation metric $U_{\text{OTR}}$ using Eq. 4b.
- **Priority:** Critical
- **Dependencies:** Environment Base, Latency & Energy models, RSU Queue Model

---

## 2. Agent Algorithms (`agents`)

### 2.1 Dueling Double DQN (`agents/d3qn.py`)
- **Purpose/Why Needed:** The primary RL decision-making agent. Implements the split network architecture:
  - Shared layers: $12 \to 256 \to 256$ (ReLU)
  - State-value stream $V(s)$: $256 \to 128 \to 1$ (ReLU)
  - Advantage stream $A(s, a)$: $256 \to 128 \to 11$ (ReLU)
  - Q-value: $Q(s, a) = V(s) + A(s, a) - \text{mean}_a(A(s, a))$
  Also handles action masking for safety tasks and exponential exploration decay.
- **Priority:** Critical
- **Dependencies:** 12-D Observation Builder, Action Mapper

### 2.2 Prioritized Experience Replay (PER) (`agents/replay.py`)
- **Purpose/Why Needed:** Stores transitions and samples them according to TD-error magnitude (using hyperparameters $\alpha=0.6$, $\beta$ scaling from $0.4 \to 1.0$) to stabilize D3QN training.
- **Priority:** Critical
- **Dependencies:** None

### 2.3 Federated Learning Aggregator (FedAvg) (`agents/federated.py`)
- **Purpose/Why Needed:** Synchronizes model weights across vehicle agents every 50 steps:
  $$w \leftarrow \sum_k \frac{n_k}{N} w_k$$
  with participation threshold $\ge 70\%$.
- **Priority:** High
- **Dependencies:** Dueling Double DQN

### 2.4 Baseline Implementations (`agents/baselines.py`)
- **Purpose/Why Needed:** Recreates non-RL and RL comparative baselines:
  - **Fixed baselines:** `AllOffload` (a=8) and `NoOffload` (a=0)
  - **wu2021:** UCB bandit on action subset $\{0, 2, 8, 10\}$
  - **yun2022:** Genetic Algorithm (GA)
  - **jing2019:** Lyapunov-based optimizer (single RSU at 1000m)
  - **shao2025:** CoopEC (Federated Coop Offloading)
  - **Restricted modes:** DQN without PER, on subset actions
- **Priority:** High
- **Dependencies:** Environment Base, Action Mapper

### 2.5 MADDPG Upper Bound Agent (`agents/maddpg.py`)
- **Purpose/Why Needed:** Centralized Training, Decentralized Execution (CTDE) continuous-action upper bound for comparison.
- **Priority:** Medium (Optional / Post-Baseline Freeze)
- **Dependencies:** Environment Base

---

## 3. Training & Evaluation Pipeline (`run`)

### 3.1 Scenario Simulator Runner (`run.py` or `main.py`)
- **Purpose/Why Needed:** Runs scenarios (`urllc`, `balanced`, `compute`), sweeps vehicle counts $N \in \{2, 4, 8, 16, 20, 32\}$, schedules Phase 1 (100 training episodes) and Phase 2 (5 evaluation episodes), and sets episode-level seeds. Exports statistics to JSON/CSV.
- **Priority:** Critical
- **Dependencies:** Environment Base, Agents, Baselines

### 3.2 Post-Processing & Figure Generation (`plot.py`)
- **Purpose/Why Needed:** Aggregates metric outputs across seeds (0-4), computes means and 95% Confidence Intervals, and outputs paper-faithful figures and tables (e.g. system utility, energy, and queue-loss vs N).
- **Priority:** High
- **Dependencies:** Scenario Simulator Runner outputs

---

## 4. Advanced/Phase-2 Components (MA-ROPE+)

### 4.1 Differential Privacy (DP) Aggregator
- **Purpose/Why Needed:** Implements Laplace or Gaussian noise perturbation on weights during Federated Learning averaging to protect user privacy under various privacy budgets $\epsilon$.
- **Priority:** Low (Phase 2 - After Baseline Freeze)
- **Dependencies:** Federated Learning Aggregator (FedAvg)

### 4.2 Mobility & Handover Realism Enhancements
- **Purpose/Why Needed:** Incorporates complex RSU handover logic and more realistic SUMO mobility traces.
- **Priority:** Low (Phase 2 - After Baseline Freeze)
- **Dependencies:** Environment Base
