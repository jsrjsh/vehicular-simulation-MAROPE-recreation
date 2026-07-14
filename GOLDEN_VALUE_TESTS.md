# GOLDEN_VALUE_TESTS.md

This document presents hand-calculated expected values for the deterministic physical links, queue backlogs, cost models, rewards, actions, and observations, serving as the benchmark for our golden-value verification tests in [`tests/test_env.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/tests/test_env.py).

---

## 1. Physical Wireless Links (at $d = 100.0$ meters, $v = 30.0$ m/s, $X_{\text{shadow}} = 0.0$ dB)

### 1.1 LTE (RAT index 1)
* **Path Loss ($PL$):**
  $$PL = 47.9 + 10 \log_{10}(100.0 / 10.0) = 57.9000 \text{ dB}$$
* **Doppler frequency ($f_D$) & Fading ($L_{\text{fade}}$):**
  $$f_D = \frac{30.0 \times (1.8 \times 10^9)}{3 \times 10^8} = 180.0 \text{ Hz}$$
  $$T_c = \frac{0.423}{180.0} \approx 0.00235 \text{ s}$$
  $$r = \min(0.1 / T_c, 10.0) = 10.0$$
  If fading envelope $A$ is mocked to $1.0$:
  $$L_{\text{fade}} = [-20 \log_{10}(1.0)] \cdot \min(10/5, 1.5) = 0.0 \text{ dB}$$
* **SINR:**
  $$\text{SINR} = 23.0 - 57.9 - (-110.0) + 0.0 - 0.0 = 75.1000 \text{ dB}$$
* **Link success probability ($p$):**
  $$p = \frac{1}{1 + \exp(-(75.1 - 4.0) / 12.0)} \approx 0.9973$$

### 1.2 ITS-G5 (RAT index 2)
* **Path Loss ($PL$):**
  $$PL = 47.9 + 10 \log_{10}(10.0) = 57.9000 \text{ dB}$$
* **Fading ($L_{\text{fade}}$):** Profile is constant $\implies L_{\text{fade}} = 0.0$ dB.
* **SINR:**
  $$\text{SINR} = 23.0 - 57.9 - (-90.0) + 0.0 - 0.0 = 55.1000 \text{ dB}$$
* **Link success probability ($p$):**
  $$p = \frac{1}{1 + \exp(-(55.1 - 4.0) / 12.0)} \approx 0.9981$$

### 1.3 WiFi-6 (RAT index 3)
* **Path Loss ($PL$):**
  $$PL = 40.05 + 20 \log_{10}(5.0 / 2.4) + 20 \log_{10}(100.0) = 86.4251 \text{ dB}$$
* **Fading ($L_{\text{fade}}$):** Constant fading $\implies L_{\text{fade}} = 0.0$ dB.
* **SINR:**
  $$\text{SINR} = 20.0 - 86.4251 - (-90.0) + 0.0 - 0.0 = 23.5749 \text{ dB}$$
* **Link success probability ($p$):**
  $$p = \frac{1}{1 + \exp(-(23.5749 - 5.0) / 9.0)} \approx 0.8873$$

### 1.4 5G-NR (RAT index 4)
* **Path Loss ($PL$):**
  $$PL = 32.4 + 20 \log_{10}(3.5) + 20 \log_{10}(100.0) = 83.2801 \text{ dB}$$
* **Doppler frequency ($f_D$) & Fading ($L_{\text{fade}}$):**
  $$f_D = \frac{30.0 \times (3.5 \times 10^9)}{3 \times 10^8} = 350.0 \text{ Hz}$$
  $$T_c = \frac{0.423}{350.0} \approx 0.00121 \text{ s}$$
  $$r = \min(0.1 / T_c, 10.0) = 10.0$$
  If fading envelope $A$ is mocked to $1.0$:
  $$L_{\text{fade}} = 0.0 \text{ dB}$$
* **SINR:**
  $$\text{SINR} = 23.0 - 83.2801 - (-110.0) + 0.0 - 0.0 = 49.7199 \text{ dB}$$
* **Link success probability ($p$):**
  $$p = \frac{1}{1 + \exp(-(49.7199 - 4.0) / 12.0)} \approx 0.9783$$

---

## 2. Latency & Energy Costs (for a Safety Task at $d=100$m, speed 30m/s, $Q=0$)
Task: $C = 1 \times 10^8$ cycles, $data = 0.1$ MB, $D = 100$ ms, $\alpha = 0.7, \beta = 0.3$.

### 2.1 Pure Local Compute (Action 0)
* **Latency ($L_{\text{total}}$):**
  $$L_{\text{local}} = \frac{10^8 \text{ cycles}}{2 \times 10^9 \text{ Hz}} \times 1000 = 50.0000 \text{ ms}$$
* **Energy ($E$):**
  $$E = P_{\text{cpu}} \cdot \frac{50.0}{1000} = 2.0 \times 0.05 = 0.1000 \text{ Joules}$$

### 2.2 5G-NR 100% Offload (Action 8)
* **Adapted offload ratio ($\rho'$):**
  Assuming equal SINR, $q_{\text{5g}} = 1.0 \implies \rho' = 1.0$.
* **Latency:**
  $$L_{\text{local\_part}} = 50.0 \times (1 - 1.0) = 0.0 \text{ ms}$$
  $$L_{\text{remote}} = 0.1 \text{ MB} \times 1.0 \times \frac{0.5 \times 10^{-3}}{1.5} \times 1000 = 0.0333 \text{ ms}$$
  $$L_{\text{offload}} = 1.0 \text{ ms (from RAT latency table)}$$
  $$L_{\text{total}} = \max(0.0, 0.0333 + 0 + 1.0) = 1.0333 \text{ ms}$$
* **Energy:**
  $$E_{\text{tx}} = \frac{0.8 \text{ mJ/MB} \times 0.1 \text{ MB} \times 1.0}{1000} = 0.00008 \text{ Joules}$$
  $$E = P_{\text{cpu}} \cdot \frac{1.0333}{1000} + E_{\text{tx}} = 2.0 \times 0.0010333 + 0.00008 = 0.002147 \text{ Joules}$$

---

## 3. RSU Queue Backlogs ($N=4$ vehicles)

* **Below Saturation:** 1 vehicle offloads with action 4 ($\rho = 0.25$) $\implies Q = 0.25$. Queuing delay $L_{\text{queue}} = 0.25 \times 50 = 12.5$ ms.
* **At Saturation:** 4 vehicles offload with action 5 ($\rho = 0.50$) $\implies Q = 2.0$. Queuing delay $L_{\text{queue}} = 2.0 \times 50 = 100.0$ ms.
* **Above Saturation:** 4 vehicles offload with action 8 ($\rho = 1.0$) $\implies Q = 4.0$. Queuing delay $L_{\text{queue}} = 4.0 \times 50 = 200.0$ ms.
  CBR index = $\text{clip}(4.0/4.0, 0.0, 1.0) = 1.0$.

---

## 4. Rewards (Training Utility $U_{\text{PRR}}$)
For vehicle 0 with local task: $L = 50.0$ ms, $E = 0.10$ J, $D = 100$ ms, $PRR_{\text{emp}} = 1.0$, $\Delta \text{CBR} = 0.0$, $\alpha = 0.7, \beta = 0.3$.
$$L / D = 50.0 / 100.0 = 0.5$$
$$E / 3.0 = 0.10 / 3.0 \approx 0.0333$$
$$U_{\text{PRR}} = 0.7 \times 1.0 + \frac{0.3}{2} e^{-0.5} + \frac{0.3}{2} e^{-0.0333} + 0.0$$
$$U_{\text{PRR}} = 0.70 + 0.15 \times 0.6065 + 0.15 \times 0.9672 = 0.70 + 0.09098 + 0.14508 = 0.9361$$
Expected utility = $0.9361$.
