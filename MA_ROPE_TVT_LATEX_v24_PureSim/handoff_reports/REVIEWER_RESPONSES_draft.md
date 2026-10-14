# Draft replies to the three faculty questions (2026-10-13, Claude Sonnet 5.5)
Evidence comes from the simulator code (verified to reproduce the paper's baseline numbers exactly), the paper source and
`MA_ROPE_Grok/codebase/results/b1/`. Figure numbers follow the latest build (Fig. 1 = waterfall, Fig. 9 = MEC queue contention).

## Q1. "With such high-speed links, how do we get 830 ms latency?"
**What the 830 ms is.** Not link latency. Measured decomposition for AllOffload (5 evaluation episodes, mean over vehicle-steps):

| fleet | mean latency | queue part | RSU backlog |
|---|---|---|---|
| N=8 | 234 ms | 233 ms (99%) | 4 units x 50 ms |
| N=16 | 436 ms | 434 ms (100%) | 8 units x 50 ms |
| N=32 | 813 ms (830 ms in Table VIII, which averages active tasks) | 812 ms (100%) | 16 units x 50 ms |

Link latency for 5G-NR is a fixed 1 ms; remote compute is 0.25-2.5 ms (0.5 ms/MB). Link throughput is not used in the latency formula at all.
Mechanism: with all N vehicles offloading 100% to the two RSUs, each RSU holds N/2 offloaded tasks in a step; each unit of backlog adds 50 ms
(`delay_per_unit_ms`), so latency is about 25 ms x N. This is the shared-queue contention the paper is about.

**Suggested reply.** "The latency is dominated by queueing at the shared MEC server, not by the radio link. 5G-NR contributes about 1 ms. When every vehicle offloads,
each of the two RSUs serves N/2 tasks in the same step and the edge server processes them in sequence with an effective service time of 50 ms per task (20 tasks/s
per RSU), so the last task waits N/2 x 50 = 800 ms at N=32. This is exactly the contention collapse of single-RAT full offloading, and MA-ROPE avoids it by keeping most
tasks local."

**Weak points to fix before sending (the faculty may find them).**
1. The paper says the queue is M/M/1 with mu = 1000 tasks/s (Sec. III-D, IV-D.4). With mu = 1000 tasks/s the delay would be about 1 ms. The code uses a linear backlog model, 50 ms per unit. The text must describe the actual model: L_queue = B_r x tau, tau = 50 ms (mu_eff = 20 tasks/s).
2. Transmission time V/BW (Eq. 3a) is not simulated. For the record, the omitted delay would be 4-40 ms at 1 Gbps for 0.5-5 MB, but 80-800 ms at LTE's 50 Mbps. State this as a simplification.
3. tau = 50 ms is a calibration constant with no cited source; justify it as the per-task MEC service time, or cite a measurement.

## Q2. "Utility for AllOffload differs between Fig. 1 and Fig. 9"
| where | AllOffload utility | what it is |
|---|---|---|
| Fig. 1 (waterfall) | 0.8166 | historical pre-correction ablation at N=8 (the caption says so), older code, not part of the corrected campaign |
| Fig. 9 (queue contention) | 0.916 for one vehicle with no queue model, 0.676 for 8 co-located vehicles | controlled queue ablation, source script not found |
| Fig. 7 (utility vs fleet size) | U_OTR 0.303 at N=8 | deadline utility, active tasks, older campaign (2026-08-03) |
| Table VIII | U_PRR 0.6022 at N=32 | training utility, corrected campaign |

They are different experiments, utilities (U_PRR vs U_OTR) and code versions, so they are not supposed to match. But the paper does not make that clear, and neither 0.8166 nor 0.916 can be reproduced with the current simulator.
My recomputation with the corrected simulator (AllOffload U_PRR, mean over vehicle-steps, one RSU): queue model off, 0.76-0.78 for 1-8 vehicles; queue model on, 0.73 (1 vehicle) falling to 0.62 (8 vehicles).
The shape matches Fig. 9 (decline with co-located vehicles), the level does not.

**Suggested reply.** "Fig. 1 is a historical ablation from before the simulator corrections and uses a different composite utility; Fig. 9 is a separate controlled queue experiment. They are not the same quantity. We will remove Fig. 1, regenerate Fig. 9 with the corrected simulator (AllOffload U_PRR 0.73 for one vehicle falling to 0.62 for eight co-located vehicles) and label every utility as U_PRR or U_OTR."

## Q3. "Table II and Table V differ in some cases"
| item | Table II | Table V | simulator code |
|---|---|---|---|
| WiFi-6 rate | 600 Mbps | 1200 Mbps | 600 Mbps (not used in latency) |
| 5G-NR rate | 1 Gbps | 2000 Mbps | 1000 Mbps (not used in latency) |
| ITS-G5 fading | Constant | Jakes, f_d = 50 Hz | constant |
| WiFi-6 fading | Constant | Jakes, f_d = 30 Hz | constant |
| 5G-NR fading | Jakes | Saleh-Valenzuela, f_d = 200 Hz | Jakes (no Saleh-Valenzuela anywhere in the code) |
| Doppler | not given | fixed f_d per RAT | computed from speed x carrier frequency / c |
| Coverage range | not given | 1000 / 300 / 100 / 300 m | not modelled in the simulator |
LTE (50 Mbps, Jakes) and ITS-G5 (27 Mbps) rates agree. Table II (delay 20/10/5/1 ms, noise floors, fading type) matches the simulator; Table V does not.

**Suggested reply.** "Table II lists the parameters actually used by the simulator; Table V gave nominal standard values for context and is inconsistent in the WiFi-6/5G-NR rates and the fading models. We will remove Table V (or label it 'nominal, not used') and keep Table II as the single parameter table." (The Track B copy of the paper already labels it "Alternate RAT Parameter Summary (non-operational)".)

## Related finding to be aware of before replying
The Evidence tracker shows the paper-reward MA-ROPE policy makes zero offload attempts when exploration is off, so the reported OTR comes from evaluation exploration. A careful reviewer asking about latency may follow up with "why does MA-ROPE's latency (226 ms) equal NoOffload's (234 ms)?". The honest answer is that it mostly executes locally. See MA_ROPE_Grok/status/B1_FINDINGS.md.

---
## Update 2026-10-14: what was changed in the paper (build MA_ROPE_TVT_v24_PureSim_20261014-0914_LATEST, 15 pages)
- Table V removed (file moved to tables_removed/). Table II is the only RAT parameter table; the channel-model paragraph now says Jakes for LTE/5G-NR, constant for ITS-G5/WiFi-6.
- Queue model rewritten (Sec. III-D and IV-D): L_queue = tau x Q_r, tau = 50 ms, a calibration constant; M/M/1 and mu = 1000 tasks/s removed; transmission time stated as not simulated; local CPU corrected to 2 GHz; "queue discretized to 8 levels" removed.
- Fig. 1 (waterfall) and its subsection removed, plus every sentence that pointed to it.
- Queue-contention figure regenerated from the corrected simulator (make_fig9_data.py, make_fig9_plot.py, results_fig9/): AllOffload with shared queue 0.722 (1 vehicle) -> 0.619 (8); without queue model about 0.77; NoOffload about 0.96; MA-ROPE 0.95-0.96.
- NEW NUMBERING for the faculty's PDF: Table V no longer exists (old VI->V ... old XIV->XIII); figures: 1 topology, 2 system model, 3 speed, 4 PRR, 5 link failure, 6 utility vs fleet, 7 fleet OTR, 8 queue contention (old Fig. 9), 9 Jakes, 10 pies, 11 training.
- NOT fixed (not in the reviewer questions): Methodology eq. (6) reward still differs from the code (U_PRR); Fig. 9 (Jakes) and Figs. 10-11 are still the clipped originals.
