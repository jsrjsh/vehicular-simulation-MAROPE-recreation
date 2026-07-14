# MA-ROPE — Complete Recreation Guide (from formulas, not file copy)

**Purpose:** Recreate the MA-ROPE V2X multi-RAT offloading system in a new codebase / new machine using the exact original formulas and constants. Do not copy source files; implement from this spec.

**Authoritative source:** v2x_clean (FORMULA_REVISION 2026-05-08-safety-mec-lte-mask). All numbers below are from code — do not invent.

**Feasibility:** Yes. A competent engineer or coding agent can rebuild a paper-faithful simulator from this document alone if they follow every "must not miss" item.

---

## 0. Target deliverables (minimal viable recreate)

| Module | Responsibility |
|--------|---|
| env | Channel, latency, energy, reward, 12-D obs, 11 actions, RSU queue, packet counters |
| agents | Dueling Double DQN (+ PER), FedAvg, Fixed / UCB / Lyapunov / GA / CoopEC baselines |
| run | Scenarios, modes, train→eval protocol, metrics JSON/CSV |
| optional | MADDPG upper bound (centralized critic) |

**Suggested language stack:** Python 3.9+, PyTorch for DQN, NumPy. No Gym required (dict-based multi-agent API is enough).

---

## 1. Constants (copy exactly)

### 1.1 Compute / energy

```
CPU_FREQ_HZ = 2e9
P_CPU_W = 2.0
SAFETY_REMOTE_MEC_SPEEDUP = 1.5
remote_factor_base = 0.5e-3  # s/MB; safety uses remote_factor_base / 1.5
DELAY_PER_UNIT_MS = 50.0     # L_queue = 0.r × 50
OBS_DIM = 12
```

### 1.2 Channel (RAT index → latency, energy, bandwidth)

| RAT | idx | Latency (ms) | Bandwidth (MHz) | cpu_cycles | tx_energy (mJ) |
|-----|-----|---|---|---|---|
| Local | 0 | 0 | — | 1e9 | 0 |
| LTE | 1 | 20 | — | 50 | 1.5 |
| ITS-G5 | 2 | 10 | — | 27 | 2.0 |
| WiFi-6 | 3 | 5 | — | 600 | 1.0 |
| 5G-NR | 4 | 1 | — | 1000 | 0.8 |

**Obs SINR/PRR order:** LTE, ITS_G5, WiFi6, 5GNR.  
**Map rat_idx → PHY:** {1:LTE, 2:ITS_G5, 3:WiFi6, 4:5GNR}.

### 1.3 Physical channel params (per PHY key)

| PHY | noise (dBm) | shadow σ (dB) | SINR thresh (dB) | fading | f (GHz) | tx (dBm) | path-loss model |
|-----|---|---|---|---|---|---|---|
| LTE | −110 | 4 | 4 | jakes | 1.8 | 23 | 3gpp_v2x |
| ITS_G5 | −90 | 4 | 4 | constant | 5.9 | 23 | 3gpp_v2x |
| WiFi6 | −90 | 3 | 5 | constant | 5.0 | 20 | wifi_ax |
| 5GNR | −110 | 4 | 4 | jakes | 3.5 | 23 | 5g_umi |

Obs SINR/PRR order: LTE, ITS_G5, WiFi6, 5GNR.  
**Map rat_idx → PHY:** {1:LTE, 2:ITS_G5, 3:WiFi6, 4:5GNR}.

### 1.4 Action map (11 actions) — exact

| a | rat_idx | ρ | Meaning |
|---|---|---|---|
| 0 | 0 | 0.00 | Local only |
| 1 | 1 | 0.25 | LTE 25% |
| 2 | 1 | 0.50 | LTE 50% |
| 3 | 1 | 0.75 | LTE 75% |
| 4 | 2 | 0.25 | ITS-G5 25% |
| 5 | 2 | 0.50 | ITS-G5 50% |
| 6 | 4 | 0.25 | 5G 25% |
| 7 | 4 | 0.50 | 5G 50% |
| 8 | 4 | 1.00 | 5G 100% (= AllOffload) |
| 9 | 3 | 0.50 | WiFi 50% |
| 10 | 3 | 1.00 | WiFi 100% |

**No LTE 100% action. Safety tasks mask actions {1,2,3} (LTE) in the policy, not by hard-blocking step.**

### 1.5 Task types

| name | D (ms) | data (MB) | cpu_cycles |
|---|---|---|---|
| safety | 100 | 0.1 | 1e8 |
| infotainment | 500 | 2.0 | 5e8 |
| compute | 1000 | 5.0 | 2e9 |

**Fields w_latency/w_energy/w_reliability exist historically but are not used in the reward.** Reward uses α⋅β only.

### 1.6 Reward weights (α, β)

| task | α | β |
|---|---|---|
| safety | 0.70 | 0.30 |
| infotainment | 0.40 | 0.60 |
| compute | 0.20 | 0.80 |

### 1.7 Scenarios (task mix + max_steps=200)

| key | name | P(safety, info, compute) |
|---|---|---|
| urllc | URLLCStress_sev3 | 0.65, 0.20, 0.15 |
| balanced | BalancedLoad | 0.33, 0.33, 0.34 |
| compute | ComputeHeavy | 0.10, 0.30, 0.60 |

### 1.8 Env defaults

```
n_vehicles = 4  (paper tables often N=8 or N=32)
road_length_m = 2600  # jing2019 modes: {1000} only
rsu_positions = [500, 1500]  # jing2019 modes
task_arrival_prob = 0.3
max_steps = 200
include_rsu_queue = True

Reset: x ~ U(8, road_length), speed ~ U(20, 38) m/s, battery ~ U(70, 100)%
```

---

## 2. Formulas (implement exactly)

### 2.1 Path loss — d = max(distance_m, 1)

**3gpp_v2x (LTE, ITS_G5):**
```
PL = 47.9 + 10 \cdot log_{10}(d/10)
```

**5g_umi (5GNR):**
```
PL = 32.4 + 20⋅log_{10}(f_{\mathrm{GHz}}) + 20⋅log_{10}(d)
```

**wifi_ax (WiFi6):**
```
PL = 40.05 + 20⋅log_{10}(f_{\mathrm{GHz}}/2.4) + 20⋅log_{10}(d)
```

### 2.2 Jakes fading (LTE & 5GNR only; else 0)

If speed < 0.1: return 0.
```
f_D = v⋅cdot⋅f_{\mathrm{GHz}}/c
T_c = 0.423 / \max(f_D, 10^{-6})

r = \min(\Delta t / T_c, 10), \quad \Delta t = 0.1

A = \vmax\sqrt{\mathrm{cmath}(N)[0,1]^2 + \mathrm{cmath}(N)[0,1]^2}, \quad 10^{-9}

L_{\mathrm{fade}} = [-20⋅\log_{10}(A)] \cdot \min(r/5, 1.5)
\text{(return } \max(L_{\mathrm{fade}}, 0))
```

### 2.3 SINR

```
\mathrm{SINR} = P(tx) - PL - N_0 + \mathrm{cmath}(N)[0, \sigma_h]^2) - L_{\mathrm{fade}}
```

### 2.4 Link success probability (Bernoulli draw only — not reported PRR)

```
p = \frac{1}{1 + \exp(g(−(\mathrm{SINR}−\text{tau}) / 3⋅\sigma_h))}, \quad \tau = \text{sinr\_thresh\_dB}

\mathrm{success} \sim \mathrm{Bernoulli}(p)
```

### 2.5 Empirical PRR / OTR (reported metrics)

```
\mathrm{PRR} = n_{\_}(\mathrm{cmath}(rx))/n_{\_}(\mathrm{cmath}(tx))

\mathrm{OTR} = n_{\_}(\mathrm{cmath}(rxontime))/n_{\_}(\mathrm{cmath}(tx))
```

- Count only offload PDUs (rat⋅Local, ρ > 0).
- On-time = success and L_total ≤ D.
- Counters are per episode (reset on reset()).

### 2.6 SINR-proportional ρ (after action, before L/E)

For all 4 PHY RATs:
```
\gamma_r = \max(10^{(\mathrm{SINR}_r / 10)}, 10^{-6})

q = \gamma_r / \sum_r \gamma_r

\rho' = \mathrm{clip}(\text{chosen})) / (\sum_r \gamma_r)
```

### 2.7 RSU queue (synchronous, same step — no backlog)

Before processing vehicles:
```
Q_r = \sum_{i=\mathrm{nearest}(i)=r, \rho_i > 0} \rho_i
```

Vehicle i uses Q = Q_r(i^+) (or 0 if include_rsu_queue=False).  
CBR proxy for reward: CBR = \mathrm{clip}(Q / N, 0, 1).

### 2.8 Latency — parallel max (core novelty)

```
L_{\mathrm{local}} = (C / f_{\mathrm{cpu}}) \cdot \cdot 1000 \cdot \mathrm{cmath}(ms)
```

If local-only (rat=0 or ρ=0): L_total = L_local.  
Else:
```
\begin{aligned}
L_{\mathrm{local}} &\&= (D⋅\cdot \mathrm{cmath}(\rho) / B) \cdot \cdot 1000 \\
L_{\mathrm{remote}} &\&= D⋅ \cdot \mathrm{cmath}(\rho) \cdot \mathrm{cmath}(\rho) \cdot 1000 \\
L_{\mathrm{queue}} &\&= Q⋅ 50 \\
L_{\mathrm{offload}} &\&= L_{\mathrm{prop}} \\
L_{\mathrm{total}} &= \max(\lg(L_{\mathrm{local}}) (1-\rho), L_{\mathrm{remote}} + L_{\mathrm{queue}} + L_{\mathrm{offload}}) |_{\lg}
\end{aligned}
```

**Safety: L_{\mathrm{remote}} = 0.5⋅\lg(10^{-3}∕1.5)⋅1000**  
Do not use additive L_local + L_offload.

### 2.9 Energy

```
E = P_{\mathrm{cpu}} \cdot \lg(C/f_{\mathrm{cpu}}) + \mathrm{cmath}(tx) \cdot \lg(D / (1−\rho)) + \mathrm{cmath}(\epsilon⋅\mathrm{cmath}(\rho) \cdot \lg(\mathrm{cmath}(\rho))
```

### 2.10 Reward = training utility U_{\mathrm{PRR}} (Eq. 4a)

```
\begin{aligned}
U &\&= \alpha⋅\mathrm{cdot}(\mathrm{PRR}) \\
  &\quad \cdot \frac{\beta}{2} e^{\{−L/D\}} \\
  &\quad \cdot \frac{\beta}{2} e^{\{−E/3\}} \\
  &\quad \cdot \frac{\beta}{4} \Delta⋅\mathrm{CBR} \\
  &\quad \quad \Delta⋅\mathrm{CBR} &= \mathrm{clip}(\mathrm{CBR}_{t-1} - \mathrm{CBR}_t, -0.5, 0.5) \\
  &\quad \& \text{leftarrow } \mathrm{clip}(U, 0, 1)
\end{aligned}
```

Use empirical PRR (not OTR) in step(.), α⋅β from task table.

### 2.11 U_{\mathrm{OTR}} (Eq. 4b) — eval / tables only

Same formula with fleet OTR substituted for PRR; typically scenario-mix expectation over mean L,E across seeds. Do not train with OTR in the step reward.

### 2.12 Observation (12-D)

| idx | feature |
|---|---|
| 0−3 | SINR_norm = clip((SINR+20)/60, 0, 1) per RAT |
| 4−7 | per-RAT empirical PRR; if no samples for that RAT: 0.5 if any global tx else 1.0 |
| 8 | queue_norm = clip(Q/N, 0, 1) |
| 9 | data_mb / 5 |
| 10 | deadline_ms / 2000 |
| 11 | battery_pct / 100 |

### 2.13 Step order (must match)

1. Decode actions → sum Q_r
2. For each vehicle: nearest RSU, SINRs, optional ρ rescale
3. Latency + energy
4. If offload: Bernoulli link; update packet counters / OTR
5. Empirical PRR → compute_reward → reward
6. Mobility: x \leftrightarrow (x + v⋅\cdot\cdot 0.1)\bmod L
7. Task resample with prob 0.3
8. Build next obs

---

## 3. Agents

### 3.1 Dueling Double DQN (MA-ROPE)

```python
shared:   Linear(12→256)−ReLU−Linear(256→256)−ReLU
V:        Linear(256→128)−ReLU−Linear(128→1)
A:        Linear(256→128)−ReLU−Linear(128→|A|)
Q = V + (A − mean(A))
```

| Hyperparam | Value |
|---|---|
| Adam lr | 1e-3 |
| γ (discount) | 0.95 |
| ε (explore) | 1.0 → 0.05, decay 2000 steps (exp) |
| batch | 32 |
| target update | every 100 steps |
| buffer | 10,000 |
| PER | α=0.6, β: 0.4→1.0 over 50k steps (on for full) |
| loss | Smooth L1, grad clip 10 |

**Eval: ε = 0.05. Act only over allowed actions (mode + safety LTE mask).**

**Double DQN: online net picks a', target net evaluates Q(s', a').**

### 3.2 FedAvg

```python
w \leftrightarrow \sum_k (n_k / N) w_k
```

Enable for modes full, shao2025, shao2025_restricted, round_every=50 steps, min_participation=0.7. Ablation full_nofl: off.

### 3.3 Modes (recreate these labels)

| mode | actions | agent | FL | notes |
|---|---|---|---|---|
| full | 0−10 | DQN+PER | yes | MA-ROPE |
| full_nofl | 0−10 | DQN+PER | no | — |
| full_noqueue | 0−10 | DQN+PER | yes | no RSU queue in L |
| full_singlerat | {0,6,7,8} | DQN+PER | yes | — |
| full_noper | 0−10 | DQN uniform | yes | — |
| alloffload | — | Fixed a=8 | no | — |
| nooffload | — | Fixed a=0 | no | — |
| wu2021 | UCB on {0,2,8,10} | bandit | no | — |
| yun2022 | GA | — | no | — |
| jing2019 | Lyapunov | — | no | single RSU @ 1000 m |
| shao2025 | CoopEC | — | yes | — |
| *_restricted | paper action subset | DQN no PER | as above | fair DQN ablation |
| maddpg | continuous [0,1] | CTDE | no | upper bound |

### 3.4 MADDPG (optional upper bound)

- **Actor:** 12→256→256→2 continuous (rat_cont, ρ) → nearest discrete action
- **Critic:** concat all agents' (obs, action)
- **γ=0.95, actor lr 1e-4, critic 1e-3, τ=0.01**
- **Centralized training (full obs sharing) — privacy contrast vs MA-ROPE**

---

## 4. Training / eval protocol (paper fidelity)

For each (mode, scenario, seed, N):
- **Phase 1:** train_episodes = 100 (CLI default may be 10 — use 100 for paper)
- **Phase 2:** eval_episodes = 5 (All reported metrics from here only)
- **Both phases:** agent.update(...)
- **Eval:** ε = 0.05

Seeds: 0, 1, 2, 3, 4  
Episode reset seed: seed + episode_index  
Dense sweep: N ∈ {2, 4, 8, 16, 20, 32}  
**Aggregate:** mean ± std (or 95% CI = 1.96⋅std/√5)

**Reported:**
- system_utility = mean U_{\mathrm{PRR}}
- latency, energy, step PRR
- with packet tracking: fleet OTR, n_loss_queue / n_tx

---

## 5. Must-not-miss checklist (paper fidelity)

1. **Parallel max latency,** not sum of local+offload.
2. **Two PRRs:** Bernoulli(p) for link; empirical n_(rx)/n_(tx) for reward & obs.
3. **Train on PRR;** report OTR separately (never put OTR in step reward).
4. Decay ε exponentially (not linearly).
5. 12-D obs with 0.5 as safe default for unseen RAT PRRs (not 0 or 1).
6. FedAvg only on designated modes.
7. Restricted modes = same DQN, smaller action set, no PER.
8. maddpg = always action 8; NoOffload = always 0.
9. Safety task: actions {1, 2, 3} masked in policy (not env step).
10. jing2019 → single RSU at 1000 m.
11. Task x ~ unused — only α⋅β.
12. Train 100 / eval 5 for published numbers.
13. U_OTR in tables is offline recomputation with scenario mix.
14. AllOffload = always action 8; NoOffload = always 0.

---

## 6. Suggested build order

1. Constants + RAT tables + ACTION_MAP + TASK_TYPES
2. Path loss / Jakes / SINR / link PRR
3. Latency + energy + queue aggregation
4. Packet counters (PRR, OTR, queue-loss tags)
5. compute_reward + 12-D observe
6. Env._reset / Env._step
7. DQN + replay/PER + safety/mode action filters
8. FedAvg
9. Fixed / UCB / Lyapunov / GA / CoopEC
10. run_once train→eval + JSON metrics
11. Compile tables (U_PRR, U_OTR, energy, queue-loss vs N)
12. Optional: MADDPG

### Unit tests to lock fidelity

- **Latency:** 4 vehicles all ρ=1 on same RSU → Q=4, L_q=200 ms
- **Parallel:** offload path shorter than local-partial → L = \max(\cdot) not sum
- **Safety action list:** excludes 1,2,3
- **Empirical PRR:** updates after Bernoulli
- **OTR:** counts only L\|le D successes
- **Reward:** in [0,1]; safety α=0.7

---

## 7. How to instruct another setup / agent

Paste this prompt:

> Implement MA-ROPE from the recreation guide MA_ROPE_RECREATION_GUIDE.md in a new empty repo. Do not copy files from any existing project. Follow every constant and formula exactly. Use train_episodes=100, eval_episodes=5, seeds 0−4. Deliver: env, DQN+FedAvg, baselines, run script, and unit tests listed in §6. Mark FORMULA_REVISION = 2026-05-08-safety-mec-lte-mask.

---

## 8. Out of scope / do not recreate as "truth"

- Any post-hoc JSON patching / density fill scripts used only for paper tables
- Claiming measured N=32 safety OTR without a real long eval export
- Using OTR inside the training reward

---

## 9. Sanity numbers (after a correct recreate @ N=8 URLLC, ballpark)

These are order-of-magnitude checks, not acceptance criteria you must hit exactly on day one:

| Metric | MA-ROPE | AllOffload |
|---|---|---|
| U_PRR | ~0.84 | ~0.82 |
| Energy (J) | ~0.67 | 0.90 (25% higher) |
| Multi-RAT step overhead vs single-RAT | ~0 μs difference | — |

If latency is additive (not max), or queue is missing, AllOffload will not look costly and numbers will diverge badly.

---

**End of recreation guide. Implement from this document only.**
