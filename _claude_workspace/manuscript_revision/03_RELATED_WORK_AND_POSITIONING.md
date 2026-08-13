# Related Work / Positioning Section (Revision Draft v1)

Built from real, cited search results in `LITERATURE_POSITIONING_REPORT.md`. Organized the way a
Related Work section should read: by sub-problem, ending in an explicit gap statement that maps
directly onto Contribution 1.

---

### 6.1 Federated learning for vehicular edge computing

Federated deep reinforcement learning has been applied to joint task-offloading and resource-
allocation in MEC-assisted vehicular networks, combining centralized and distributed DDPG-style
training to reduce non-IID drift across vehicles while preserving raw-data privacy (Journal of
Network and Computer Applications, 2024). More recent work extends this to heterogeneous,
dependency-structured (DAG) task graphs via a federated meta-RL framework with graph-attention and
sequence-to-sequence policy modeling (FedMAGS, arXiv 2605.18437, 2026), targeting fast adaptation
across distributed MEC servers. These systems address *what to offload and where*, under
federation, but treat the radio link as a single channel or a resource-allocation variable rather
than a multi-technology choice — they do not select among heterogeneous RATs.

### 6.2 Multi-RAT selection and traffic steering

Learned RAT selection has been studied primarily in cellular traffic-steering contexts: a
hierarchical reinforcement learning approach for 5G multi-RAT traffic steering reports 8.49-12.52%
higher throughput and 27.74-39.13% lower delay versus plain DQN and threshold heuristics (arXiv
2301.05316 and its HRL follow-up). This confirms multi-RAT selection is a live, currently-published
DRL problem with quantified gains over simpler baselines — but the unit of decision is a cellular
user session, not a vehicle's per-task offloading decision, and the systems are not federated or
privacy-constrained. Non-learned multi-RAT selection is also an active area in industry practice:
issued patents (Verizon US10616830B2/US11330516B2; US12445926) cover RAT selection based on
traffic pattern, coverage, and load signals, and SON-assisted optimization in virtualized RAN — all
rule-based or classically-optimized, network-side, and not RL-driven per-agent decisions.

### 6.3 Privacy-preserving federated learning in vehicular networks

Local differential privacy applied to federated learning in vehicular/VANET settings is an active,
separate line of work — e.g., LDP-protected federated infrastructures for VANETs and correlated-DP
personalized federated learning for autonomous driving. A related but distinct patent direction
(US20220250656A1) addresses *which vehicles are selected to participate* in federated training
rounds, not what those vehicles learn to do with the trained policy. Privacy protection and
per-agent RAT/offload decision-making have not, in the sources surveyed, been combined in one
system.

### 6.4 D3QN and prioritized experience replay for offloading

Dueling Double DQN with prioritized experience replay remains an actively-published architecture
choice for offloading decisions as recently as 2024-2025 (e.g., P-D3QN for edge-assisted IIoT task
offloading, IEEE Xplore 10660558), confirming this is a current, defensible architectural choice
for MA-ROPE's per-agent policy rather than a dated one — the contribution here is not the base
learner but its federated, multi-RAT, privacy-constrained application.

### 6.5 The gap this work fills

No system surveyed combines all four elements MA-ROPE integrates: (i) per-vehicle heterogeneous
RAT selection, (ii) a continuous, channel-adaptive offload ratio rather than a binary or discrete
resource split, (iii) federated (FedAvg) training across vehicles rather than a single centralized
policy, and (iv) a local-differential-privacy budget on shared updates. Each element individually
is established in the literature; the combination — and the specific fleet-scale reliability
finding it produces (Section 5.2) — is not.

### 6.6 Honest limitation of this positioning

This is a targeted scan (documented queries, representative results), not a systematic literature
review with a PRISMA-style protocol. We do not claim exhaustiveness. A venue that will scrutinize
novelty claims closely should be given a more exhaustive pre-submission search; nothing in this
section depends on that additional search coming back empty, but it is honest due diligence worth
doing before final submission, not before this draft.
