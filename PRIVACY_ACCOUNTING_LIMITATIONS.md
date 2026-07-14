# PRIVACY_ACCOUNTING_LIMITATIONS.md

This document outlines the privacy accounting boundaries and composition limitations of the current Local Differential Privacy (LDP) implementation.

---

## 1. Scope of Current Privacy Guarantee

* **Guaranteed Privacy Boundary:** Per-round Local $(\epsilon, \delta)$-Differential Privacy for each individual client weight submission.
* **Composition across Rounds:** Not formally composed. The configured $\epsilon$ represents a **per-aggregation-round nominal epsilon**. Cumulative privacy loss across multiple communication rounds is not tightly computed or bounded by a global budget.
* **Subsampling Amplification:** Not modeled. While only a subset of clients participate in each round (based on $P_{\text{participate}}$), the amplification effects on the privacy budget are not accounted for.
* **Random client participation:** Treated as a round-level dropout; composition models assume client participation is deterministic for privacy bookkeeping.

---

## 2. Requirements for a Publishable Cumulative Privacy Claim

To elevate this round-level guarantee to a publishable, globally-bounded cumulative privacy proof, the following cryptographic and mathematical mechanisms must be integrated:

1. **Rényi Differential Privacy (RDP) Accountant:**
   * Implement Rényi composition to compute the tight cumulative privacy budget $(\epsilon_{\text{total}}, \delta_{\text{total}})$ over $T$ communication rounds. Standard composition bounds (e.g. Advanced Composition) are loose, whereas RDP composition provides tight bounds for the Gaussian mechanism:
     $$\epsilon_{\text{total}}(\alpha) = T \cdot \epsilon_{\text{round}}(\alpha)$$
2. **Amplification by Client Subsampling:**
   * Account for Poisson subsampling or random sample selections. Under random client sampling, the effective round epsilon $\epsilon_{\text{round}}$ is amplified by the participation ratio $q = \frac{K}{N}$ (e.g., $q \approx 0.70$):
     $$\epsilon_{\text{eff}} \approx q \cdot \epsilon_{\text{round}}$$
3. **Global Composition Bookkeeper:**
   * Introduce a privacy accountant module (e.g. `MomentAccountant` or `Opacus` style RDP composition scheduler) that dynamically terminates training if cumulative privacy loss exceeds a globally configured target budget $\epsilon_{\text{target}}$.
