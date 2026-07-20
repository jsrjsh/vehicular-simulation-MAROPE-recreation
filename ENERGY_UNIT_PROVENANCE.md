# ENERGY UNIT PROVENANCE AUDIT

## 1. Local CPU Energy
- **Variable Name:** `P_CPU_W`
- **Configured Value:** `2.0`
- **Intended Physical Unit:** Watts (J/s)
- **Source in Guide:** Config section 1.1 "Local CPU power consumption (Watts)"
- **Mathematical Use:** Multiplied by local execution latency (in seconds) to compute energy.
- **Output/Reporting Unit:** Joules (J). For a 50ms task, energy = $2.0 \times 0.05 = 0.1$ J.

## 2. Radio Transmit Energy Coefficient
- **Variable Name:** `tx_energy_mj` (or historically $\epsilon$)
- **Configured Values:** LTE: 1.5, ITS-G5: 2.0, WiFi6: 1.0, 5GNR: 0.8
- **Intended Physical Unit:** mJ/MB (milliJoules per Megabyte transmitted)
- **Source in Guide:** Table 1.2 "tx_energy (mJ)" - However, the mathematical implementation `tx_energy_mj * task["data_mb"]` dictates that the coefficient is treated as a per-megabyte rate.
- **Source-code Location:** `env/config.py` lines 42-77, and `env/environment.py` line 295.
- **Mathematical Use:** `e_tx = tx_energy_mj * data_mb * rho_prime`
- **Output/Reporting Unit:** Mathematically, multiplying (mJ/MB) $\times$ (MB) yields **milliJoules (mJ)**.

## 3. Remote Execution Energy
- **Variable Name:** Not explicitly tracked on the vehicle side.
- **Mathematical Use:** Remote MEC energy consumption is intentionally excluded from the vehicle's local energy metric, aligning with standard edge offloading formulations where the vehicle only pays the radio transmission energy cost.

## 4. Total Task Energy
- **Variable Name:** `e_total`
- **Source-code Location:** `env/environment.py` line 296
- **Mathematical Use:** `e_total = P_CPU_W * (l_local * (1.0 - rho_prime) / 1000.0) + e_tx`
- **Output/Reporting Unit:** The code blindly adds `e_tx` (which is in milliJoules) to the CPU energy term (which is in Joules). Consequently, **`e_total` contains a massive unit defect**. It treats mJ values as if they were J, effectively inflating the transmission energy cost by a factor of 1000.

## 5. Summary Conclusion
The configured RAT coefficient `tx_energy_mj` represents **mJ per MB**. 
The lack of a `/ 1000.0` conversion in the `e_tx` addition is a confirmed unit defect. A 5 MB transmission over 5G (0.8 mJ/MB) correctly requires 4.0 mJ of energy, but the simulator mathematically processes it as 4.0 Joules.
