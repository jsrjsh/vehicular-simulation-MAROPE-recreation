# LDP_PARAMETER_PROVENANCE.md

This document traces the origin of all Local Differential Privacy (LDP) parameters to identify whether they are specified by the **Recreation Guide**, the **Manuscript**, or are **Engineering Assumptions**.

---

## 1. Parameter Provenance Matrix

| LDP Parameter | Value | Primary Source | Provenance Analysis & Documentation |
| :--- | :--- | :--- | :--- |
| **Privacy Mode** | `none`, `ldp_gaussian` | User Request / Guide | Mode selection (`none` or `ldp_gaussian`) to control LDP pipeline activation. |
| **Clipping Norm ($C$)** | Configurable (Default `1.0` or `5.0`) | Engineering Assumption | Sensitivity boundary to bound client update influence. Chosen dynamically to prevent clipping too much signal while bounding extreme weights. |
| **Nominal Epsilon ($\epsilon$)** | $\{0.1, 0.5, 1.0, 2.0, 5.0, 10.0\}$ | User Request / Spec | Defines the nominal round-level privacy loss budget. |
| **Delta ($\delta$)** | `1e-5` | User Request / Spec | Probability of privacy guarantee failure. |
| **Gaussian Mechanism Conversion** | $\sigma = \frac{\sqrt{2 \ln(1.25/\delta)}}{\epsilon}$ | Engineering Assumption | Standard mathematical conversion mapping $(\epsilon, \delta)$ to Gaussian noise multiplier $\sigma$ for the classical Gaussian mechanism. |
| **Local Update Calculation** | $\Delta_i = w_i - w_{\text{global}}$ | Engineering Assumption | Standard difference-vector update formulation to privatize parameter changes rather than raw weights. |
| **Zero-mean Gaussian** | $\mathcal{N}(0, \sigma^2 C^2 I)$ | Recreation Guide / Spec | Noise perturbation added to client updates. |
| **Independence Seeds** | Client and round-based | Engineering Assumption | Seeding using $client\_id + round \times 1000$ to prevent cross-client or cross-round noise correlation. |
