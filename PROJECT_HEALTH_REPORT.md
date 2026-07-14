# PROJECT_HEALTH_REPORT.md

This document presents the initial health assessment of the MA-ROPE simulation platform reconstruction project.

---

## 1. Executive Summary

| Metric | Score / Status | Description |
| :--- | :--- | :--- |
| **Current Completeness** | **0% (Implementation)**<br>**100% (Specification)** | No source files have been written yet, providing a clean-slate starting point. Reference specifications are fully frozen. |
| **Technical Debt** | **0% (None)** | No legacy code exists. Design choices can be kept completely aligned with clean modular architectures. |
| **Architecture Quality** | **Excellent (Planned)** | The decoupled design (`config` $\to$ `channel` $\to$ `env` $\to$ `agents` $\to$ `run`) prevents spaghetti code and isolates concerns. |
| **Research Reproducibility** | **9.5 / 10** | High score due to the exactness of mathematical formulas and hyperparameters in the Recreation Guide. |
| **Estimated Effort** | **~28 Hours** | Approx. 3-5 days of focused engineering to achieve baseline replication and verification. |
| **Project Risk Level** | **Low-Medium** | Primarily numerical/formulaic divergence risks, manageable via strict Stage 1 unit tests. |

---

## 2. Detailed Health Metrics

### 2.1 Current Completeness
- **Specification:** 100% complete. The guide contains all physical, channel, compute, reward, and hyperparameter specifications.
- **Codebase:** 0% complete. No Python code is currently present in the repository.
- **Verification Suites:** 0% complete. Unit tests are planned but not yet written.

### 2.2 Technical Debt
- Because this project starts from a clean directory, we have **zero technical debt**.
- To prevent debt accumulation during implementation, we will enforce:
  - Strict separation between physical channel logic (`channel.py`) and vehicular state logic (`environment.py`).
  - Configuration constants externalized to `config.py` (no magic numbers in formulas).
  - Rigid, independent test coverage on environment equations before introducing PyTorch agents.

### 2.3 Architecture Quality
The planned architecture is modular and decoupled:
- **Configuration Layer:** Centralized parameters ensuring single-source-of-truth.
- **Physical Modeling Layer:** Standard stateless math functions (path loss, Doppler shift, fading) returning deterministic outputs.
- **Environment State Machine:** Handles vehicle kinematics, task generation, and steps.
- **Agent Policy Layer:** Separates RL models (D3QN, PER) from non-RL algorithms (Lyapunov, GA, UCB) using a clean, standardized step interface.
- **Evaluation Pipeline:** Standardized JSON exports that prevent post-hoc data tampering.

### 2.4 Research Reproducibility Score (9.5 / 10)
- **Strengths:** 
  - Exact formulas for path loss models across LTE, 5G-NR, and WiFi-6 are provided.
  - Action map (11 distinct actions) and scenario configurations are fully specified.
  - Hyperparameters for D3QN and PER match the paper's optimization setups.
- **Remaining Minor Risks (0.5 deduction):**
  - Minor numerical deviations could occur depending on how the Jakes fading model's random coefficients are initialized.
  - Exact details of the CoopEC baseline (shao2025) logic may require close alignment to match paper outcomes.

---

## 3. Estimated Effort Remaining

| Phase | Tasks | Hours |
| :--- | :--- | :--- |
| **Phase 1: Environment & Channel** | Implement configs, path loss, Jakes fading, and parallel-max latency/energy. | 8 |
| **Phase 2: Mechanics & State** | Implement RSU queues, packet tracking, PRR/OTR counters, reward, and 12-D obs. | 6 |
| **Phase 3: Stage 1 Unit Tests** | Write and execute all environment verification tests. | 4 |
| **Phase 4: RL Agents & PER** | Implement D3QN network, PER buffer, policy action masking, and FedAvg. | 6 |
| **Phase 5: Baselines** | Implement Fixed, UCB, Lyapunov, CoopEC, and GA policies. | 6 |
| **Phase 6: Runner & Plots** | Implement scenario simulation runner and plot generation scripts. | 4 |
| **Total Estimated Effort** | | **34 Hours** |

*Note: Distributed over 4-5 working days of focused reconstruction.*

---

## 4. Major Risks & Mitigation Strategies

### Risk 1: Additive Latency Computation Error
- **Impact:** High. If latency components ($L_{\text{local}}$ and $L_{\text{offload}}$) are summed instead of evaluated using the parallel-max formulation, offloading will always appear inferior to local execution, and system utility values will drop significantly below paper numbers.
- **Mitigation:** A dedicated unit test in `tests/test_env.py` will verify that offload paths shorter than local-partial paths evaluate to the parallel max, not their sum.

### Risk 2: Action Masking vs. Environment Step Hard-Blocking
- **Impact:** High. If safety tasks are prevented from offloading to LTE by hard-blocking the actions in the environment step, the agent will learn incorrect state transition dynamics.
- **Mitigation:** Safety task action masking will be enforced strictly in the policy action selection step (masking Q-values of actions $\{1, 2, 3\}$ to $-\infty$ during training and evaluation), leaving the environment transition function general.

### Risk 3: OTR vs. PRR Reward Contamination
- **Impact:** Medium. If the On-Time Ratio (OTR) is used in the training reward instead of the empirical Packet Reception Ratio (PRR), training will become highly unstable because OTR is a discontinuous step function dependent on hard deadline thresholds.
- **Mitigation:** The reward function $U_{\text{PRR}}$ will strictly use empirical PRR (calculated per RAT per episode) as specified in Eq. 4a. OTR will be compiled solely as an evaluation metric in post-processing.
