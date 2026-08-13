import os

base_dir = "MA_ROPE/MASTER/MA_ROPE_MASTER_v21/sections"

# Task 2 & 4: Strengthen U_OTR & Statistical interpretation
with open(os.path.join(base_dir, "results_part1.tex"), "r") as f:
    res1 = f.read()

otr_para = r"""

While some centralized baselines marginally exceed MA-ROPE in scalar $U_{OTR}$ (e.g., MADDPG by 0.009 at N=32), operational deployment decisions in vehicular edge computing cannot optimize for deadline compliance alone. Maximizing $U_{OTR}$ often requires centralized observation sharing and incurs prohibitive energy costs (34.0\% higher for MADDPG). Instead, deployment viability depends on a balanced framework that scales under dense conditions without exhausting vehicular batteries or crashing RSU queues. By trading a negligible $U_{OTR}$ decrease for substantial improvements in Fleet OTR scalability, queue stability, and energy efficiency under a decentralized privacy-preserving FedAvg architecture, MA-ROPE presents a more robust solution for real-world heterogeneous V2X networks."""

res1 = res1.replace("A sensitivity analysis of these weights is left for future work.", "A sensitivity analysis of these weights is left for future work." + otr_para)

stat_sent = " Given the stochastic nature of the environment, small numerical differences at the third decimal place should not be over-interpreted; rather, the principal conclusions are drawn from the consistent scaling trends across vehicle densities and aggregated metrics."
res1 = res1.replace("(0.7057 J vs. 0.9441 J).", "(0.7057 J vs. 0.9441 J)." + stat_sent)

res1 = res1.replace("under SAE J3016.", r"under 3GPP V2X safety requirements~\cite{molina2017}.")

with open(os.path.join(base_dir, "results_part1.tex"), "w") as f:
    f.write(res1)


# Task 3: Justify Custom Simulator
with open(os.path.join(base_dir, "experiments.tex"), "r") as f:
    exp = f.read()

sim_para = r"""
Although standard network simulators such as ns-3, Veins, or SUMO provide comprehensive full-stack emulation, evaluating federated multi-agent reinforcement learning across heterogeneous RATs requires tight, synchronous coupling between the physical environment and the distributed training loop. We therefore implemented a custom Python-based V2X simulator tailored for algorithmic evaluation and fast DRL inference. To ensure fidelity, the physical-layer behavior rigorously follows established standards, including 3GPP TR 38.901 for cellular fading and IEEE 802.11ax for WiFi. This design choice emphasizes the validation of the multi-agent decision surface and offloading orchestration rather than introducing a new generalized network simulator.

"""
exp = exp.replace(r"\subsection{Experimental Setup}", r"\subsection{Experimental Setup}" + sim_para)

with open(os.path.join(base_dir, "experiments.tex"), "w") as f:
    f.write(exp)


# Task 5: Latency Citation Review
with open(os.path.join(base_dir, "system_model.tex"), "r") as f:
    sys = f.read()

sys = sys.replace("(SAE J3016 Level 4)", r"(e.g., 3GPP TR 36.885~\cite{molina2017})")
sys = sys.replace("SAE J3016 workloads.", r"3GPP V2X safety workloads.")
sys = sys.replace("Safety V2X (SAE J3016 Level 4)", r"Safety V2X (3GPP TR 36.885)")

with open(os.path.join(base_dir, "system_model.tex"), "w") as f:
    f.write(sys)


# Task 6: Novelty Statement
with open(os.path.join(base_dir, "abstract.tex"), "r") as f:
    abs_tex = f.read()

abs_orig = "To our knowledge, MA-ROPE is the first V2X framework to combine multi-RAT selection, SINR-proportional partial offload, shared MEC queue contention, dual PRR/OTR utility reporting, and federated DRL in one simulation framework."
abs_new = "These results demonstrate MA-ROPE's capability to effectively integrate multi-RAT heterogeneity, shared queue contention, and federated learning into a unified V2X offloading solution."
abs_tex = abs_tex.replace(abs_orig, abs_new)

with open(os.path.join(base_dir, "abstract.tex"), "w") as f:
    f.write(abs_tex)

print("Scientific polish applied.")
