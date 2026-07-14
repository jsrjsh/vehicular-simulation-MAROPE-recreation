# AMBIGUITIES.md

This document records all mathematical, physical, and implementation ambiguities identified between the manuscript draft, recreation guide, and LaTeX renderings, alongside their engineering resolutions.

---

## 1. Typeset Rendering Artifacts in Latency and Energy Equations

### Conflict / Ambiguity
The LaTeX renderings in Sections 2.8 and 2.9 featured log terms:
* **Compute energy:** $P_{\text{cpu}} \cdot \lg(C/f_{\text{cpu}})$
* **Transmission energy:** $\mathrm{cmath}(tx) \cdot \lg(D / (1-\rho))$
* **Latency:** $\max(\lg(L_{\text{local}})(1-\rho), \dots)$

Evaluating these terms literally using base-10 or natural logarithms would lead to:
1. Negative compute energy, since $C/f_{\text{cpu}}$ is typically less than 1.0 (e.g. 0.05 s for safety tasks), and $\log_{10}(0.05) \approx -1.3$.
2. Division-by-zero errors when offloading fully ($\rho = 1.0$), since $D / (1 - \rho)$ becomes $D / 0$.
3. Indeterminate results when executing locally ($\rho = 0.0$), since $\log(0.0) = -\infty$.

### Resolution
By evaluating the physical constraints of computing and energy, we resolved these LaTeX typesetting artifacts as follows:
* **Local Computing Energy:** Evaluated as $P_{\text{cpu}} \cdot (1 - \rho') \cdot \frac{C}{f_{\text{cpu}}}$ (Joules), representing power multiplied by local computation time.
* **Transmission Energy:** Evaluated as $\frac{E_{\text{tx}} \cdot D \cdot \rho'}{1000}$ (Joules), representing the energy spent transmitting the offloaded data fraction over the selected wireless interface.
* **Idle/Waiting Energy:** To match the paper's sanity energy values (e.g., ~0.90 J for AllOffload and ~0.67 J for MA-ROPE), the vehicle must consume compute power $P_{\text{cpu}} = 2.0$ W during the waiting phase of the task. Thus, total energy is modeled as:
  $$E = P_{\text{cpu}} \cdot \frac{L_{\text{total}}}{1000} + \frac{E_{\text{tx}} \cdot D \cdot \rho'}{1000} \quad \text{(Joules)}$$
  If $\rho' = 0$ (local execution), this simplifies exactly to $P_{\text{cpu}} \cdot (C / f_{\text{cpu}})$ Joules. If $\rho' > 0$, it correctly scales with the parallel latency $L_{\text{total}}$ and transmission energy.

---

## 2. Jakes Fading Doppler Frequency Carrier Scaling

### Conflict / Ambiguity
The Doppler frequency is specified as $f_D = v \cdot f_{\text{GHz}} / c$. Since carrier frequencies $f_{\text{GHz}}$ are given in GHz (e.g. 1.8 for LTE), leaving the term unscaled (not converting GHz to Hz) yields:
$$f_D = \frac{30 \times 1.8}{3 \times 10^8} = 1.8 \times 10^{-7} \text{ Hz}$$
This leads to coherence times of $T_c \approx 423,000$ seconds, making fading completely static.

### Resolution
We converted carrier frequencies from GHz to Hz by multiplying by $10^9$:
$$f_D = \frac{v \cdot (f_{\text{GHz}} \cdot 10^9)}{c}$$
For $v = 30$ m/s and LTE at 1.8 GHz, this yields a physical Doppler shift of $180$ Hz and a coherence time of $T_c \approx 2.35$ ms, which is standard for vehicular sidelink channels.

---

## 3. Log-Normal Shadowing Formula in SINR

### Conflict / Ambiguity
The SINR formula in Section 2.3 includes the term `+ cmath(N)[0, sigma_h]^2)`. Squaring a Gaussian variable in decibels makes shadowing strictly positive (non-zero mean), which violates standard zero-mean log-normal shadowing models.

### Resolution
We resolved the formula to use a standard zero-mean normal random variable:
$$X_{\text{shadow}} \sim \mathcal{N}(0, \sigma_h^2)$$

---

## 4. Link Success Exponent Variable `g`

### Conflict / Ambiguity
The link success sigmoid formula features a parameter `g`:
$$p = \frac{1}{1 + \exp(g(-(\text{SINR} - \tau) / 3\sigma_h))}$$
No value is defined for `g`.

### Resolution
Treated `g` as $1.0$, which yields a standard sigmoid activation representing the transmission success rate over the SINR margin.

---

## 5. Task Workload Resampling Kinematics

### Conflict / Ambiguity
Section 2.13 states "Task resample with prob 0.3". It was not specified if a task is processed over multiple steps, or if the entire task is processed and completed within a single simulation step.

### Resolution
Because task latencies (100 ms to 1000 ms) are evaluated instantly within a single step to compute empirical PRR/OTR, tasks are completed in a single slot. "Task resample with prob 0.3" means that at each step, a new task type is generated with 30% probability, and with 70% probability the vehicle continues with the same task type for the next step.

---

## 6. RSU Queue Aggregation

### Conflict / Ambiguity
Section 2.7 has $Q_r = \sum \rho_i$ but it wasn't clear if it sums the original $\rho_i$ or adapted $\rho'_i$.

### Resolution
Summed the original chosen action ratios $\rho_i$ at the start of the step (matching the step order where Decode Actions happens before SINR adaptation). This represents the workload offloading request queue size.

---

## 7. Battery Consumption

### Conflict / Ambiguity
No battery capacity or decay formula is specified, though initial battery percentage is $U(70, 100)\%$.

### Resolution
The battery percentage is held constant at its initial reset value (since task energy consumption of ~1 J is microscopic compared to standard vehicle battery capacities).
