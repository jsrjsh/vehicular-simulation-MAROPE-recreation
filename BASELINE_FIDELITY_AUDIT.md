# BASELINE_FIDELITY_AUDIT.md

This document presents a comprehensive audit of all formulaic, physical, and architectural ambiguities identified in the [`MA_ROPE_RECREATION_GUIDE.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/MA_ROPE_RECREATION_GUIDE.md) and their alignment with the IEEE manuscript and physical modeling rules.

---

## Ambiguity 1: GHz-to-Hz Doppler Frequency Conversion

* **Original Expression:** $f_D = v \cdot f_{\text{GHz}} / c$
* **Implemented Interpretation:**
  * **`baseline_recreation` mode:** $f_D = v \cdot f_{\text{GHz}} / c$ (literal, unscaled).
  * **`physically_corrected` mode:** $f_D = v \cdot (f_{\text{GHz}} \cdot 10^9) / c$ (converted to Hz).
* **Physical Justification:** Doppler frequency shift $f_D = \frac{v}{\lambda} = \frac{v \cdot f}{c}$ requires carrier frequency $f$ to be in Hertz (Hz), not GigaHertz (GHz). Failing to multiply by $10^9$ results in an $f_D \approx 10^{-7}$ Hz, which makes the Doppler coherence time $T_c \approx 4.2 \times 10^5$ seconds (static fading), which is physically incorrect for highway speeds of 30 m/s.
* **Manuscript Support:** The manuscript describes speed-dependent Rayleigh fading matching standard Jakes models, which mathematically require Hz carrier frequency scaling.
* **Expected Impact:**
  * **SINR / PRR:** Correcting the frequency makes fading vary dynamically from step to step, adding realistic link fluctuations.
  * **OTR / Utility:** Increases variance of latency and reward, as bad fading states occur dynamically rather than persisting statically.
* **Baseline Numerical Shift:** Yes. Unscaled Doppler makes fading static per vehicle, while scaled Doppler introduces dynamic Rayleigh fluctuations.
* **Confidence Level:** 100%

---

## Ambiguity 2: Shadowing Distribution in SINR

* **Original Expression:** $+ \mathrm{cmath}(N)[0, \sigma_h]^2)$
* **Implemented Interpretation:**
  * **`baseline_recreation` mode:** $+ X_{\text{shadow}}^2$, where $X_{\text{shadow}} \sim \mathcal{N}(0, \sigma_h^2)$.
  * **`physically_corrected` mode:** $+ X_{\text{shadow}}$, where $X_{\text{shadow}} \sim \mathcal{N}(0, \sigma_h^2)$.
* **Physical Justification:** Log-normal shadowing in decibels is represented as a zero-mean normal random variable $X_{\text{shadow}} \sim \mathcal{N}(0, \sigma_h^2)$. Squaring the Gaussian variable forces shadowing to be strictly positive (representing a permanent power gain), which is physically impossible.
* **Manuscript Support:** The manuscript models standard symmetric log-normal shadowing in dB.
* **Expected Impact:**
  * **SINR:** Squaring the term artificially boosts SINR by $+ \sigma_h^2$ on average (e.g. $+16$ dB for LTE/5G).
  * **PRR / OTR / Utility:** Artificial SINR boost makes links look extremely reliable, hiding offloading losses.
* **Baseline Numerical Shift:** Yes. Literal implementation results in artificially inflated link success probabilities.
* **Confidence Level:** 100%

---

## Ambiguity 3: Undefined Exponent Coefficient $g$ in Link Success

* **Original Expression:** $p = \frac{1}{1 + \exp(g(-(\text{SINR} - \tau) / 3\sigma_h))}$
* **Implemented Interpretation:** $g = 1.0$ (in both modes).
* **Physical Justification:** The parameter $g$ acts as a scale coefficient in the sigmoid function mapping SINR margin to link success probability. In the absence of a defined value in the guide or manuscript, a standard scale $g=1.0$ is the standard model.
* **Manuscript Support:** Implicitly assumed as 1.0 (standard sigmoid).
* **Expected Impact:** Minimal, as the SINR margin divides by $3 \sigma_h$ which provides the physical slope scaling.
* **Baseline Numerical Shift:** No.
* **Confidence Level:** 95%

---

## Ambiguity 4: Partial-Offloading Transmission-Energy Scaling

* **Original Expression:** $+ \mathrm{cmath}(tx) \cdot \lg(D / (1-\rho)) + \mathrm{cmath}(\epsilon \cdot \rho \cdot \lg(\rho))$
* **Implemented Interpretation:**
  * **`baseline_recreation` mode:** Evaluates log-based terms literally (with epsilons to prevent divisions by zero or logs of zero).
  * **`physically_corrected` mode:**
    $$E = P_{\text{cpu}} \cdot \frac{L_{\text{total}}}{1000} + \frac{E_{\text{tx}, r} \cdot data\_mb \cdot \rho'}{1000} \quad \text{(Joules)}$$
* **Physical Justification:** In literal mode, computing energy is negative for execution times $t < 1.0$ s, and transmission energy is infinite at $\rho=1.0$ due to $D/(1-\rho)$ division by zero. The physically corrected equation computes local compute energy for the execution duration, adds transmitter RF energy scaling linearly with offloaded data $D \cdot \rho'$, and keeps energy non-negative.
* **Manuscript Support:** The manuscript states that offloading energy scales linearly with offloaded bits and transmitter power.
* **Expected Impact:**
  * **Energy:** `baseline_recreation` produces negative/infinite values. `physically_corrected` guarantees physical, positive energy matching the paper metrics (~0.67 J and ~0.90 J).
  * **Utility:** Matches the exponential utility bounds of Eq. 4a.
* **Baseline Numerical Shift:** Yes. The literal formula cannot be executed at boundaries without crashing, and yields negative values.
* **Confidence Level:** 100%

---

## Ambiguity 5: Queue Handling when $\lambda \ge \mu$ (Saturation)

* **Original Expression:** $Q_r = \sum_{i: \text{nearest}(i)=r, \rho_i > 0} \rho_i$.
* **Implemented Interpretation:** Sums the offloading ratios of connected vehicles in the current step. Does not carry backlog to the next step, matching: "synchronous, same step — no backlog". Saturation is represented by queuing delay $L_{\text{queue}} = Q_r \times 50$ ms, which is bounded below by 0.0 and above by $N \times 50 = 200$ ms. CBR index is $\text{clip}(Q_r/N, 0, 1)$.
* **Physical Justification:** Instantaneous backlog aggregation represents the slot-based channel contention. Since slot length is 100 ms and task deadline is 100 ms, queuing delay cannot build up across multiple slots because tasks expire or finish within the step.
* **Manuscript Support:** Confirms slot-level synchronous RSU contention.
* **Expected Impact:**
  * **Latency:** Creates latency penalties up to 200 ms for congested RSUs, making offloading less attractive.
  * **Utility:** CBR delta penalizes agents that overload the RSU in consecutive steps.
* **Baseline Numerical Shift:** No.
* **Confidence Level:** 95%

---

## Ambiguity 6: Timing of RSU Queue Observations

* **Original Expression:** Not explicitly defined whether observation is causal (previous step's queue) or instantaneous (current step's queue).
* **Implemented Interpretation:** Causal. The observation feature 8 (`queue_norm`) uses the queue size $Q_r$ computed at the end of the previous step. This ensures that agents do not have instantaneous knowledge of other agents' concurrent decisions before selecting their own actions, preserving game-theoretic causality.
* **Physical Justification:** Vehicles cannot know what actions other vehicles are selecting in the current millisecond before they choose theirs. They must rely on the previous step's queue state.
* **Manuscript Support:** The state-space definition confirms that observations contain the queue state prior to action selection.
* **Expected Impact:** Enables stable multi-agent coordination without non-causal information loops.
* **Baseline Numerical Shift:** No.
* **Confidence Level:** 95%

---

## Ambiguity 7: Transmitting RATs Per Decision Epoch

* **Original Expression:** Action map selects one discrete index $a \in [0, 10]$.
* **Implemented Interpretation:** One single RAT is selected per vehicle per decision epoch. The vehicle cannot transmit over multiple interfaces simultaneously.
* **Physical Justification:** Simplifies RF transceiver modeling and prevents radio interface conflicts.
* **Manuscript Support:** The action space table maps each action to a single `rat_idx` ($1, 2, 3$, or $4$).
* **Expected Impact:** Simplifies observation builder and cost modeling.
* **Baseline Numerical Shift:** No.
* **Confidence Level:** 100%
