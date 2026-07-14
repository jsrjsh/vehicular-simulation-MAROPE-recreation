# LDP_THREAT_MODEL.md

This document defines the Local Differential Privacy (LDP) Threat Model for the federated D3QN vehicular simulation platform.

---

## 1. Protected Object
* **Definition:** The **local model updates** submitted by client vehicles to the central aggregation server during each synchronization round:
  $$\Delta_i = w_i - w_{\text{global\_previous}}$$
* The raw local model parameters ($w_i$) are also protected, as only the perturbed update ($\Delta_{i,\text{private}}$) is ever transmitted.

---

## 2. Adversary Model
* **Honest-but-Curious Server:** The central aggregation server follows the synchronous FedAvg protocol faithfully, but will attempt to reconstruct private vehicular trajectories and training distributions from the client update uploads.
* **Passive Eavesdroppers:** External observers intercepting wireless communication links between the vehicles and RSUs.
* **Curious Clients:** Other vehicles in the network attempt to extract information about neighboring clients by observing the broadcasted global model updates.

---

## 3. Protected Information
* **Local training samples:** The specific tuples $(s, a, r, s', done)$ logged in local experience replay buffers.
* **State attributes:** Exact vehicle velocities, positions, task data sizes, latency constraints, local channel fading coefficients, and battery capacities.
* **Location privacy:** Historical routes and task demand patterns.

---

## 4. Attacks in Scope
* **Membership Inference Attacks:** An adversary attempts to determine if a specific training sample (e.g. a safety task deadline violation under deep fading) was part of a vehicle's local optimization batch.
* **Update / Gradient Inversion Attacks:** An adversary attempts to reconstruct raw training state observations ($s$) by solving optimization inverse systems on the submitted parameter change vectors ($\Delta_i$).

---

## 5. Attacks Out of Scope
* **Malicious Poisoning (Byzantine Clients):** Vehicles submitting deliberately corrupted weight updates to degrade global accuracy.
* **Byzantine Aggregator:** A server that deviates from sample-count-weighted FedAvg.
* **Client Collusion:** Active collaboration between multiple clients to attack a target vehicle.
* **Physical Compromise:** Adversary acquiring root access to the physical CPU/memory of a client vehicle.

---

## 6. Exact Guarantee
* **Formulation:** Per-round Local $(\epsilon, \delta)$-Differential Privacy.
* **Meaning:** For any two neighboring local model updates $\Delta_i, \Delta'_i$ (where neighbor refers to updates derived from local datasets differing by at most one sample), and any set of output privatized updates $O$:
  $$\mathbb{P}(\Delta_{i,\text{private}} \in O) \le e^{\epsilon} \cdot \mathbb{P}(\Delta'_{i,\text{private}} \in O) + \delta$$
* **Parameters:** Supported bounds: $\epsilon \in [0.1, 10.0]$ per-round nominal privacy, $\delta = 1\text{e-}5$.
