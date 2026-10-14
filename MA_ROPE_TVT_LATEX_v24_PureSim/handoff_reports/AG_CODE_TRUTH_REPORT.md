# AG Code-Truth Check Report: MA-ROPE TVT Manuscript Conflicts

## Metadata
- **Vendor / Agent**: Google Antigravity (Gemini 3.8 Flash)
- **Date**: 2026-10-08
- **Job ID**: `20261005-marope-tvt-presentation-polish-a1`
- **Task**: `tasks/AG_code_truth_check.md`
- **Mode**: READ-ONLY inspection of `src/maro_pe/`, `scripts/`, `results/`, and manuscript sections. No manuscript, code, table, or result files were edited.

---

## Executive Summary
This report provides definitive, code-verified answers with exact `file:line` evidence to resolve three major contradictions in the MA-ROPE TVT manuscript, along with provenance for the experimental results in Table VIII:
1. **Reward Function**: D3QN training uses the composite utility $U_{\text{PRR}}$ (Eq. 4 / Eq. 17a). The quadratic penalty formula in Methodology IV.A Eq. (6) ($w_1 \cdot \text{OTR} - w_2 \cdot \Delta L^2 - w_3 \cdot E$) does not exist in the codebase.
2. **Action Space & Offload Ratios**: The true action space consists of 11 discrete actions mapping to $\rho \in \{0.00, 0.25, 0.50, 0.75, 1.00\}$ (local $\rho=0$ plus 4 partial/full offload levels). The theoretical action space is $|A| = 1 + 4 \times 4 = 17$, not 24.
3. **Observation Vector**: The true state is a continuous 12-dimensional vector $[\text{SINR}_{\times 4}, \text{PRR}_{\times 4}, Q, D, L, B]$. Neither the RSU queue $Q$ nor the channel fading is discretized to 8 levels in the model input.
4. **Table VIII Provenance**: The numbers (e.g., MA-ROPE 0.8274, AllOffload 0.1230 at $N=32$) were produced by campaign `_claude_workspace/results/CAMPAIGN_PHYSICS_FIX_20260818/` and summarized in `results/ns3_vs_python_comparison.csv`.

---

## Question 1: Reward Actually Used in Training

### 1. Answer
- **Training Reward**: Training in both `src/maro_pe/env/environment.py` and `scripts/train_federated.py` uses the **$U_{\text{PRR}}$ composite utility** function.
- **Exact Formula Evaluated in Code**:
  $$u = \alpha \cdot \text{PRR} + \frac{\beta}{2} \exp\left(-\frac{L}{D}\right) + \frac{\beta}{2} \exp\left(-\frac{E}{3.0}\right) + \frac{\beta}{4} \Delta\text{CBR}$$
  where reward is clamped via $r_t = \text{clip}(u, 0.0, 1.0)$.
- **Task-Adaptive Weights**: $\alpha$ and $\beta$ are task-specific constants defined in `src/maro_pe/env/config.py`:
  - Safety tasks: $\alpha = 0.70, \beta = 0.30$
  - Infotainment tasks: $\alpha = 0.40, \beta = 0.60$
  - Compute tasks: $\alpha = 0.20, \beta = 0.80$
- **Role of $U_{\text{OTR}}$**: $U_{\text{OTR}}$ is NOT used as the training reward. It is calculated in `environment.py` solely as an auxiliary metric packed into `infos[i]["u_otr"]` for logging and evaluation.
- **Status of Methodology Eq. (6)**: The formula $r_t = w_1 \cdot \text{OTR}_t - w_2 \cdot (\max(L_t - D_{\max}, 0))^2 - w_3 \cdot E_t$ with weights $(0.6, 0.3, 0.1)$ **does not exist anywhere in the codebase**. It is an orphaned, obsolete formulation.
- **Verdict**: The manuscript statement in **Section III / Algorithm 2** ($r_t = U_{\text{PRR}}$ training signal, $U_{\text{OTR}}$ evaluation metric) is **CORRECT**. The text in **Methodology IV.A Eq. (6)** is **COMPLETELY WRONG**.

### 2. Evidence (File:Line)
- `src/maro_pe/env/environment.py:332`: `# 5. Compute rewards (U_PRR training utility)`
- `src/maro_pe/env/environment.py:359-385`: Explicit reward calculation using task $\alpha, \beta$, exponential latency ratio, exponential energy ratio, and clipped $\Delta\text{CBR}$; `rewards[i] = float(np.clip(u, 0.0, 1.0))`.
- `src/maro_pe/env/config.py:124-146`: `TASK_TYPES` table setting $\alpha$ and $\beta$.
- `src/maro_pe/env/environment.py:423-437`: Computation of `u_otr` packed only into `infos[i]["u_otr"]`.
- `scripts/train_federated.py:205, 213, 218`: `next_obs_dict, rewards_dict, dones_dict, infos_dict = env.step(action_dict)` -> `reward = rewards_dict[i]` -> `agent.replay_buffer.add(state, action, reward, next_state, v_done)`.
- Global grep across repository confirms 0 occurrences of $w_1 = 0.6$ or quadratic penalty in training code.

### 3. Exact Manuscript Text to Change
In `MA_ROPE_TVT_LATEX_v24_PureSim/sections/methodology.tex` (lines 4–13):
> **Current text**:
> ```latex
> \subsection{Reward Function}
> 
> The immediate reward signal at timestep $t$ is designed to encourage deadline-compliant delivery while balancing energy:
> \begin{equation}
> \label{eq:reward_function}
> r_t = w_1 \cdot \text{OTR}_t - w_2 \cdot (\max(L_t - D_{\max}, 0))^2 - w_3 \cdot E_t
> \end{equation}
> 
> where $\text{OTR}_t$ is the dimensionless ratio of tasks completed on-time to total tasks in epoch $t$, $L_t$ is the actual task completion latency in milliseconds (including transmission, queue wait, and MEC processing), $D_{\max}$ is the URLLC deadline threshold (e.g., 100 ms), and $E_t$ is the energy consumed by transmission in epoch $t$ in joules. The weights $w_1 = 0.6$, $w_2 = 0.3$, and $w_3 = 0.1$ are normalized to a unit sum and were tuned via grid search in preliminary experiments. This formulation directly encodes deadline compliance through OTR as the primary goal, discourages marginally-late deliveries via the latency penalty, and prevents wasteful transmission strategies using the energy penalty.
> ```
> **Correction**: Replace with a reference to the composite utility $U_{\text{PRR}}$ defined in Eq. (17a) of the System Model, clarifying that $r_t = U_{\text{PRR}}$ serves as the primary reward-shaping signal during training, while $U_{\text{OTR}}$ (Eq. 17b) is evaluated as the safety deadline QoS criterion.

### 4. Confidence & Uncertainty
- **Confidence**: 100%
- **Uncertainty**: 0%

---

## Question 2: Offload-Ratio Levels and Action Count

### 1. Answer
- **True Offload Ratios**:
  $$\rho \in \{0.00, 0.25, 0.50, 0.75, 1.00\}$$
  There are **4 non-zero offload ratio levels** ($n_\rho = 4$: 0.25, 0.50, 0.75, 1.00) plus local processing ($\rho = 0.00$).
- **Exact 11-Entry `ACTION_MAP`** (from `src/maro_pe/env/config.py:108-120`):
  - `0`: `(0, 0.00)` — Local execution only ($\rho = 0.00$)
  - `1`: `(1, 0.25)` — LTE, $\rho = 0.25$
  - `2`: `(1, 0.50)` — LTE, $\rho = 0.50$
  - `3`: `(1, 0.75)` — LTE, $\rho = 0.75$
  - `4`: `(2, 0.25)` — ITS-G5, $\rho = 0.25$
  - `5`: `(2, 0.50)` — ITS-G5, $\rho = 0.50$
  - `6`: `(4, 0.25)` — 5G-NR, $\rho = 0.25$
  - `7`: `(4, 0.50)` — 5G-NR, $\rho = 0.50$
  - `8`: `(4, 1.00)` — 5G-NR, $\rho = 1.00$ (AllOffload)
  - `9`: `(3, 0.50)` — WiFi-6, $\rho = 0.50$
  - `10`: `(3, 1.00)` — WiFi-6, $\rho = 1.00$
  *(RAT index mapping: 0 = Local, 1 = LTE, 2 = ITS-G5, 3 = WiFi-6, 4 = 5G-NR).*
- **Theoretical Action Count**:
  - The theoretical unmasked action space for 4 wireless RATs with $n_\rho = 4$ offload levels is:
    $$|A| = 1 + n_{\text{RATs}} \times n_\rho = 1 + 4 \times 4 = 17$$
    (1 local action + 16 offloading pairs).
  - This is already correctly documented in Table II (`tables/table_02_action_space.tex`, row 5: $n_{\text{RATs}}=4, n_\rho=4 \implies |A|=17$).
  - The manuscript sentence claiming "6 offload ratio levels from 0.0 to 1.0 ... $|A| = 24$" is **INCORRECT**.
  - Furthermore, the sentence in Section V.A stating "2 for LTE" and "3 for WiFi-6" is inverted: the code implements **3 actions for LTE** (0.25, 0.50, 0.75) and **2 actions for WiFi-6** (0.50, 1.00).

### 2. Evidence (File:Line)
- `src/maro_pe/env/config.py:108-120`: Definitive declaration of `ACTION_MAP`.
- `src/maro_pe/env/environment.py:206-211`: Action decoding logic verifying `act_idx in ACTION_MAP` and unpacking `(rat_idx, rho)`.
- `MA_ROPE_TVT_LATEX_v24_PureSim/tables/table_02_action_space.tex:15`: Table II states $n_{\text{RATs}}=4, n_\rho=4, |A|=17$.
- `MA_ROPE_TVT_LATEX_v24_PureSim/sections/system_model.tex:66`: Line states $\rho \in \{0.25, 0.50, 0.75, 1.0\}$.

### 3. Exact Manuscript Text to Change
In `MA_ROPE_TVT_LATEX_v24_PureSim/sections/algorithm_design.tex` (line 21):
> **Current text**:
> ```latex
> where $m_t \in M$ represents the 4 RAT options (LTE, ITS-G5, WiFi-6, 5G-NR) and $\rho_t \in R$ denotes the 6 offload ratio levels from 0.0 to 1.0. This defines a theoretical action space of $|A| = 24$ potential (RAT, $\rho$) pairs. The implemented action space, however, consists of 11 discrete actions selected via strategic masking to avoid infeasible or suboptimal combinations (e.g., LTE at low offload ratios being bandwidth-limited, or ITS-G5 at full offloading exceeding its range envelope). These 11 actions include 1 action for local execution ($\rho=0$), 3 actions for 5G-NR (reliable fallback), 3 for WiFi-6 (high bandwidth, short range), 2 for ITS-G5 (V2X-specialized), and 2 for LTE (wide coverage fallback).
> ```
> **Correction**: Change "6 offload ratio levels from 0.0 to 1.0 ... $|A| = 24$" to:
> "$\rho_t \in R = \{0.25, 0.50, 0.75, 1.0\}$ denotes the $n_\rho = 4$ candidate offload ratio levels (with $\rho=0$ indicating local execution). Across the 4 wireless RATs, this defines a theoretical unmasked action space of $|A| = 1 + 4 \times 4 = 17$ actions (Table~\ref{tab:action_space}). The implemented action space prunes this to 11 discrete actions via domain constraints: 1 local execution, 3 LTE (25\%, 50\%, 75\%), 2 ITS-G5 (25\%, 50\%), 2 WiFi-6 (50\%, 100\%), and 3 5G-NR (25\%, 50\%, 100\%)."

### 4. Confidence & Uncertainty
- **Confidence**: 100%
- **Uncertainty**: 0%

---

## Question 3: Observation Vector and Queue Discretization

### 1. Answer
- **Dimension**: Exactly **12-dimensional continuous float32** vector (`OBS_DIM = 12`).
- **Elements and Scaling**:
  - Feature 0: $\text{SINR}_{\text{LTE}}$, normalized: $\text{clip}((\text{SINR}_{\text{dB}} + 20.0) / 60.0, 0.0, 1.0)$
  - Feature 1: $\text{SINR}_{\text{ITS}}$, normalized: $\text{clip}((\text{SINR}_{\text{dB}} + 20.0) / 60.0, 0.0, 1.0)$
  - Feature 2: $\text{SINR}_{\text{WiFi}}$, normalized: $\text{clip}((\text{SINR}_{\text{dB}} + 20.0) / 60.0, 0.0, 1.0)$
  - Feature 3: $\text{SINR}_{\text{5G}}$, normalized: $\text{clip}((\text{SINR}_{\text{dB}} + 20.0) / 60.0, 0.0, 1.0)$
  - Feature 4: Empirical $\text{PRR}_{\text{LTE}}$ ($n_{rx}/n_{tx}$) in $[0.0, 1.0]$
  - Feature 5: Empirical $\text{PRR}_{\text{ITS}}$ ($n_{rx}/n_{tx}$) in $[0.0, 1.0]$
  - Feature 6: Empirical $\text{PRR}_{\text{WiFi}}$ ($n_{rx}/n_{tx}$) in $[0.0, 1.0]$
  - Feature 7: Empirical $\text{PRR}_{\text{5G}}$ ($n_{rx}/n_{tx}$) in $[0.0, 1.0]$
  - Feature 8: RSU Queue $Q$, normalized: $\text{clip}(q_{\text{size}} / N_{\text{vehicles}}, 0.0, 1.0)$
  - Feature 9: Task data size $D$, normalized: $\text{task}[\text{"data\_mb"}] / 5.0$
  - Feature 10: Task deadline $L$, normalized: $\text{task}[\text{"D\_ms"}] / 2000.0$
  - Feature 11: Vehicle battery $B$, normalized: $\text{battery} / 100.0$
- **Discretization Refuted**:
  - **RSU Queue $Q$**: Not discretized to 8 levels (or any discrete bins). It is computed as a continuous sum of vehicle offload fractions $\sum \rho_i$ and scaled by fleet size.
  - **Channel State**: Not quantized to 8 levels. Continuous real-valued SINR in dB is computed from distance path loss, log-normal shadowing, and Jakes fading, and then linearly normalized into $[0, 1]$.
  - The sentence in Section IV.D.4 / Methodology line 81 ("Vehicles observe this queue length, discretized to 8 levels, every 1-second interval") is **FALSE / REFUTED**.
  - The 12-dimensional formulation in Section V.A Eq. (13) ($s = [\text{SINR}_{\times 4}, \text{PRR}_{\times 4}, Q, D, L, B]$) is **CONFIRMED**.

### 2. Evidence (File:Line)
- `src/maro_pe/env/config.py:14`: `OBS_DIM = 12`
- `src/maro_pe/env/environment.py:157-193`: Complete definition of `_build_observations()` with exact per-element normalization formulas.
- `src/maro_pe/agents/d3qn/network.py:16-21`: `DuelingQNetwork(state_dim=12, action_dim=11)` defining `Linear(12, 256)`.
- `src/maro_pe/env/channel.py:85-111`: Continuous floating-point SINR calculation without quantization.

### 3. Exact Manuscript Text to Change
In `MA_ROPE_TVT_LATEX_v24_PureSim/sections/methodology.tex` (line 81):
> **Current text**:
> ```latex
> The MEC server operates a First-In-First-Out (FIFO) queue shared among all $N$ vehicles. It has a processing capacity of $\mu = 1000$ tasks per second, with service time per task calculated based on a remote CPU frequency of 2000 MHz. The maximum queue depth is limited to 100 tasks, beyond which new submissions are dropped. Vehicles observe this queue length, discretized to 8 levels, every 1-second interval.
> ```
> **Correction**: Change the last sentence:
> "Vehicles observe this normalized queue backlog $Q \in [0, 1]$ directly within their continuous 12-dimensional state vector."

### 4. Confidence & Uncertainty
- **Confidence**: 100%
- **Uncertainty**: 0%

---

## Extra: Provenance of Table VIII Results (0.8274 MA-ROPE, 0.1230 AllOffload at N=32)

### 1. Answer
- **Originating Directory**:
  `_claude_workspace/results/CAMPAIGN_PHYSICS_FIX_20260818/`
  (and its summary counterpart in `results/ns3_vs_python_comparison.csv`).
- **Primary Aggregation File**:
  `_claude_workspace/results/CAMPAIGN_PHYSICS_FIX_20260818/CORRECTED_BASELINE_RESULTS.csv`
- **Underlying Per-Seed Runs**:
  `_claude_workspace/results/CAMPAIGN_PHYSICS_FIX_20260818/raw/n32/ma-rope_seed[0-4].csv`
  `_claude_workspace/results/CAMPAIGN_PHYSICS_FIX_20260818/raw/n32/alloffload_seed[0-4].csv`
- **Script Generating Comparison Table**:
  `scripts/compare_ns3_vs_python.py:26-29`
- **Exact Numeric Match Across 5 Seeds at $N=32$**:
  - **MA-ROPE Full**:
    - Fleet OTR: `0.827358` $\rightarrow$ **0.8274**
    - PRR: `0.938014` $\rightarrow$ **0.9380**
    - Mean Latency: `226.4913` $\rightarrow$ **226.5** ms
    - $U_{\text{OTR}}$: `0.521205` $\rightarrow$ **0.5212**
    - $U_{\text{PRR}}$: `0.955999` $\rightarrow$ **0.9560**
  - **AllOffload (5G 100%)**:
    - Fleet OTR: `0.123025` $\rightarrow$ **0.1230**
    - PRR: `0.964338` $\rightarrow$ **0.9643**
    - Mean Latency: `829.9795` $\rightarrow$ **830.0** ms
    - $U_{\text{OTR}}$: `0.125509` $\rightarrow$ **0.1255**
    - $U_{\text{PRR}}$: `0.602174` $\rightarrow$ **0.6022**
  - **CoopEC-RAT**:
    - Fleet OTR: `0.724879` $\rightarrow$ **0.7249**
    - Mean Latency: `213.7480` $\rightarrow$ **213.7** ms
  - **UCB-RAT**:
    - Fleet OTR: `0.332779` $\rightarrow$ **0.3328**
    - Mean Latency: `304.6475` $\rightarrow$ **304.6** ms
  - **NoOffload**:
    - Fleet OTR: `1.0000` $\rightarrow$ **1.0**
    - Mean Latency: `233.6699` $\rightarrow$ **233.7** ms

Every single cell of Table V and Table VIII in the manuscript matches this campaign to 4 decimal places.

### 2. Confidence & Uncertainty
- **Confidence**: 100%
- **Uncertainty**: 0%
