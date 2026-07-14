# AMBIGUITY_IMPACT_REPORT.md

This document reports the quantitative and qualitative impacts of our ambiguity resolutions on the core simulation metrics comparing **Baseline Recreation** (`baseline_recreation`) and **Physically Corrected** (`physically_corrected`) configurations.

---

## 1. Summary of Metric Impacts

| Metric | Baseline Recreation Mode Impact | Physically Corrected Mode Impact | Impact Analysis |
| :--- | :--- | :--- | :--- |
| **SINR** | Artificially inflated by shadowing variance ($+ \sigma_h^2$). LTE/5G links see $+16$ dB boost. | Physically correct path-loss, zero-mean shadowing, and Jakes fading. | Squaring shadowing in baseline mode creates a permanent positive gain, making links unrealistically strong. |
| **Latency** | Evaluates local compute component in log-scale ($\approx -1.3$). | Evaluates local and remote computation in physical milliseconds. | The parallel-max model in corrected mode correctly matches task execution paths, preventing negative latency. |
| **Energy** | Negative compute energy (e.g. $-2.6$ J) and infinite transmission energy at boundaries ($\rho=1.0$). | Strictly positive energy matching paper benchmarks (~0.67 J and ~0.90 J). | The log-based formula in baseline mode fails at boundary actions ($a=8, 10$) and violates energy non-negativity. |
| **PRR** | High success rates ($>99.9\%$) across all channels due to artificial SINR boost. | Realistic distance-dependent success rates ($97.8\%$ for 5G at 100m). | Zero-mean shadowing and dynamic fading fluctuations properly stress the multi-RAT offloading decision maker. |
| **OTR** | Inflated; does not reflect physical timing due to incorrect latency logging. | Accurately models packet delivery time constraints ($L_{\text{total}} \le D$). | Crucial metric for offloading evaluation. Successfully isolated from the step reward function. |
| **Utility ($U$)** | Diverges significantly from the $[0, 1]$ utility scale due to negative latency/energy inputs. | Strictly bounded in $[0, 1]$, matching Eq. 4a and Eq. 4b. | Ensures RL agents can train with stable gradient bounds. |

---

## 2. In-Depth Metric Analysis

### 2.1 Latency ($L$)
* **Baseline Recreation:**
  $L_{\text{total}} = \max(\log_{10}(L_{\text{local}}) (1-\rho'), L_{\text{remote}} + L_{\text{queue}} + L_{\text{offload}})$
  For a safety task ($L_{\text{local}} = 50.0$ ms), the local term evaluates to $\log_{10}(50) \cdot (1-\rho') \approx 1.7 \cdot (1-\rho')$. Because $\log_{10}(\text{ms})$ is used, the local latency component is scaled down by orders of magnitude relative to the offloading component (which is in standard milliseconds, e.g. $L_{\text{offload}} = 20.0$ ms). This makes offloading look disproportionately slow.
* **Physically Corrected:**
  $L_{\text{total}} = \max(L_{\text{local}}(1-\rho'), L_{\text{remote}} + L_{\text{queue}} + L_{\text{offload}})$
  Computes physical parallel latency in milliseconds. Local and offloaded components remain on the same scale, allowing correct decision thresholds.

### 2.2 Energy ($E$)
* **Baseline Recreation:**
  $E = P_{\text{cpu}} \cdot \log_{10}(C/f_{\text{cpu}}) + E_{\text{tx}} \cdot \log_{10}(D / (1-\rho')) + \epsilon \cdot \rho' \log_{10}(\rho')$
  For local compute, $C/f_{\text{cpu}} = 0.05$ s $\implies \log_{10}(0.05) = -1.30$. Power is 2.0 W $\implies E_{\text{local}} = -2.60$ Joules (violates energy non-negativity).
  For full offload ($\rho'=1.0$), $D / (1-\rho') \to D / 0 \to \infty$, leading to floating point overflows.
* **Physically Corrected:**
  $E = P_{\text{cpu}} \cdot \frac{L_{\text{total}}}{1000} + \frac{E_{\text{tx}} \cdot data \cdot \rho'}{1000}$
  Computes positive energy consumption. When $\rho'=0$, it simplifies to local compute energy ($0.10$ J for safety task). When offloaded, it accounts for transmitter power consumption and vehicle CPU idle power over the task latency duration, matching the paper's benchmark numbers.

### 2.3 SINR & PRR
* **Baseline Recreation:**
  $\text{SINR} = P_{\text{tx}} - PL - N_0 + X_{\text{shadow}}^2 - L_{\text{fade}}$
  Since $X_{\text{shadow}}^2$ is strictly positive, the log-normal shadowing term acts as a power amplifier. For a shadowing standard deviation of $\sigma_h = 4.0$ dB, the average SINR boost is $+16$ dB. Furthermore, unscaled Doppler frequency shift ($f_D \approx 10^{-7}$ Hz) makes fading constant, failing to capture the time-varying nature of vehicular channels.
* **Physically Corrected:**
  $\text{SINR} = P_{\text{tx}} - PL - N_0 + X_{\text{shadow}} - L_{\text{fade}}$
  Shadowing is symmetric and zero-mean ($X_{\text{shadow}} \sim \mathcal{N}(0, \sigma_h^2)$). Doppler frequency shift is properly scaled ($f_D = v \cdot f_{\text{GHz}} \cdot 10^9 / c$), leading to realistic coherence times ($\approx 2.35$ ms) and step-by-step fading variations.
