# Professor Version Changelog

## Modifications

### Task 1: Verify Remaining Manual Citations
- **Sentences modified:** None.
- **Reason:** The final search confirmed 0 manual citation brackets remained in the text following the previous formatting phase. The only remaining `[1]` was the legitimate `\begin{algorithmic}[1]`.
- **Reviewer concern addressed:** N/A.

### Task 2: Strengthen $U_{OTR}$ Discussion
- **Sentences modified/added:** `sections/results_part1.tex`
  - *Added:* "While some centralized baselines marginally exceed MA-ROPE in scalar $U_{OTR}$ (e.g., MADDPG by 0.009 at N=32), operational deployment decisions in vehicular edge computing cannot optimize for deadline compliance alone. Maximizing $U_{OTR}$ often requires centralized observation sharing and incurs prohibitive energy costs (34.0\% higher for MADDPG). Instead, deployment viability depends on a balanced framework that scales under dense conditions without exhausting vehicular batteries or crashing RSU queues. By trading a negligible $U_{OTR}$ decrease for substantial improvements in Fleet OTR scalability, queue stability, and energy efficiency under a decentralized privacy-preserving FedAvg architecture, MA-ROPE presents a more robust solution for real-world heterogeneous V2X networks."
- **Reason:** To strengthen the narrative by explaining why Fleet OTR, queue stability, and energy scalability represent the core operational metrics under dense V2X conditions compared to scalar $U_{OTR}$ alone.
- **Reviewer concern addressed:** "MA-ROPE is not always the top performer on $U_{OTR}$."

### Task 3: Justify the Custom Simulator
- **Sentences modified/added:** `sections/experiments.tex`
  - *Added:* "Although standard network simulators such as ns-3, Veins, or SUMO provide comprehensive full-stack emulation, evaluating federated multi-agent reinforcement learning across heterogeneous RATs requires tight, synchronous coupling between the physical environment and the distributed training loop. We therefore implemented a custom Python-based V2X simulator tailored for algorithmic evaluation and fast DRL inference. To ensure fidelity, the physical-layer behavior rigorously follows established standards, including 3GPP TR 38.901 for cellular fading and IEEE 802.11ax for WiFi. This design choice emphasizes the validation of the multi-agent decision surface and offloading orchestration rather than introducing a new generalized network simulator."
- **Reason:** Explicitly clarifies why standard platforms were insufficient for this specific multi-agent DRL context, while confirming physical-layer rigor.
- **Reviewer concern addressed:** "Why was a custom simulator used instead of ns-3 / Veins / SUMO?"

### Task 4: Statistical Interpretation
- **Sentences modified/added:** `sections/results_part1.tex`
  - *Added:* "Given the stochastic nature of the environment, small numerical differences at the third decimal place should not be over-interpreted; rather, the principal conclusions are drawn from the consistent scaling trends across vehicle densities and aggregated metrics."
- **Reason:** Provides a statistical caveat against over-analyzing minor numerical variations.
- **Reviewer concern addressed:** Comparisons of values differing only in the third decimal place.

### Task 5: Latency Citation Review
- **Sentences modified:** `sections/system_model.tex` and `sections/results_part1.tex`
  - *Modified:* Replaced "(SAE J3016 Level 4)" with "(e.g., 3GPP TR 36.885~\cite{molina2017})"
  - *Modified:* Replaced "SAE J3016 workloads" with "3GPP V2X safety workloads"
  - *Modified:* Replaced "Safety V2X (SAE J3016 Level 4)" with "Safety V2X (3GPP TR 36.885)"
  - *Modified:* Replaced "under SAE J3016." with "under 3GPP V2X safety requirements~\cite{molina2017}."
- **Reason:** SAE J3016 defines driving automation levels, whereas 3GPP provides the actual physical/MAC level specifications regarding the 100 ms V2X safety latency deadline.
- **Reviewer concern addressed:** Misattributed standard for the 100 ms safety deadline.

### Task 6: Novelty Statement
- **Sentences modified:** `sections/abstract.tex`
  - *Modified:* "To our knowledge, MA-ROPE is the first V2X framework to combine multi-RAT selection, SINR-proportional partial offload, shared MEC queue contention, dual PRR/OTR utility reporting, and federated DRL in one simulation framework." $\rightarrow$ "These results demonstrate MA-ROPE's capability to effectively integrate multi-RAT heterogeneity, shared queue contention, and federated learning into a unified V2X offloading solution."
- **Reason:** The "first framework" novelty claim was originally duplicated almost word-for-word between the Abstract and Introduction. The Abstract version was simplified to reduce repetitive phrasing, retaining the strong novelty claim in the Introduction.
- **Reviewer concern addressed:** Repetitive or over-claimed novelty statements.

---

## Confirmation of Scientific Constraints
I confirm that throughout this process:
- No equations changed
- No figures changed
- No tables changed
- No numerical results changed
- No algorithms changed
- No experimental data changed
