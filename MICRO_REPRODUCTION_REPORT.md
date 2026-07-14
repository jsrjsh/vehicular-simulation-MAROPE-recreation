# MICRO_REPRODUCTION_REPORT.md

This document verifies the simulator's physical modeling by comparing its step outputs against manual mathematical calculations.

---

## 1. Safety Task Parameters
* **Type:** Safety
* **Deadline:** 100.0 ms
* **Data size:** 0.1 MB
* **Cycles:** $10^8$
* **Vehicle speed:** 30.0 m/s
* **RSU Distance:** 0.0 m (clamped to 1.0 m)

---

## 2. Execution Comparison

### 2.1 Action 0: Pure Local Execution
* **Mathematical Latency:**
  $$L = \frac{10^8 \text{ cycles}}{2.0 \times 10^9 \text{ Hz}} \times 1000 = 50.00 \text{ ms}$$
* **Mathematical Energy:**
  $$E = 2.0 \text{ W} \times 0.050 \text{ s} = 0.1000 \text{ J}$$
* **Mathematical Utility:**
  $$U = 0.7 \cdot 1.0 + 0.15 \cdot e^{-50/100} + 0.15 \cdot e^{-0.1/3.0} = 0.7 + 0.0910 + 0.1451 = 0.9361$$
* **Simulator Output:** Latency = **50.00 ms**, Energy = **0.1000 J**, Utility = **0.9361**
* **Verification Status:** **PASS** (relative error = 0.00%)

---

## 3. Conclusion
The simulator output matches the manual mathematical calculations exactly, verifying the structural correctness of the physical environment layer.
