# Version log: MA-ROPE journal paper (Track A)

One file, newest first. Each row of the change tables was verified by searching the text of the three PDFs (not from memory). Files named `*_LATEST.*` are always in this folder; earlier versions are in `releases_archive/`.

| Version | Built | Pages | What it is | PDF / TeX |
|---|---|---|---|---|
| **V3** | 14 Oct 2026, 09:25 | 15 | Reward and utility text now matches the code | `MA_ROPE_TVT_v24_PureSim_20261014-0925_LATEST.pdf` / `.tex` |
| **V2** | 14 Oct 2026, 09:14 | 15 | Fixes for the three faculty questions (latency, Fig. 1 vs Fig. 9, Table II vs Table V) | `releases_archive/MA_ROPE_TVT_v24_PureSim_20261014-0914.pdf` / `.tex` |
| **V1** | 8 Oct 2026, 17:54 | 16 | Version under review (assumed to be what was sent; please confirm) | `releases_archive/MA_ROPE_TVT_v24_PureSim_20261008-1754.pdf` / `.tex` |

## What changed, version by version

| # | Change | Where | V1 | V2 | V3 |
|---|---|---|---|---|---|
| 1 | Queue delay described as M/M/1 with 1000 tasks/s | Sec. III-D, IV-D | yes | no | no |
| 2 | Queue delay described as backlog x 50 ms (a calibration constant), transmission time stated as not simulated | Sec. III-D, IV-D | no | yes | yes |
| 3 | "Local processing runs at 1000 MHz" and "queue discretized to 8 levels" | Sec. IV-D | yes | no | no |
| 4 | Table V (peak rates, coverage, Saleh-Valenzuela fading) | Methodology | yes | removed | removed |
| 5 | Channel-model text says Jakes for every RAT | Sec. IV-D.3 | yes | corrected (Jakes only for LTE and 5G-NR) | same |
| 6 | Fig. 1, contribution waterfall (AllOffload U = 0.8166) and its subsection | Related Work | yes | removed | removed |
| 7 | Queue-contention figure with AllOffload 0.916 to 0.676 and NoOffload about 0.64 | Results | yes | replaced | replaced |
| 8 | Queue-contention figure from the corrected simulator: AllOffload 0.722 to 0.619, NoOffload about 0.96, MA-ROPE 0.95 to 0.96 (5 seeds) | Results (now Fig. 8) | no | yes | yes |
| 9 | Reward given as 0.6 OTR - 0.3 (max(L-D,0))^2 - 0.1 E, "weights tuned via grid search" | Sec. IV-A | yes | yes | removed |
| 10 | Reward given as U_PRR clipped to [0,1] with task-adaptive weights; U_OTR evaluation only | Sec. IV-A | no | no | yes |
| 11 | Utility equations divided by Z = 1.25 ("Z makes the block sum to beta") | Sec. III-E, eq. (5a)-(5c) | yes | yes | removed |
| 12 | Utility equations match the code: beta/2, beta/2, beta/4 terms and a clip to [0,1] | Sec. III-E | no | no | yes |

## Results that did NOT change
All headline results are identical in V1, V2 and V3: fleet OTR 0.8274 and 0.1230 (N=32), safety OTR 0.7537, retention 0.975 and 0.367, latency 830.0 ms and 226.5 ms. The simulator code was not changed in any version; only text, tables and two figures were.

## Numbering after V2 (important if sir has V1)
- Tables: Table V no longer exists. Old Tables VI to XIV are now V to XIII. Tables I to IV are unchanged.
- Figures: old Fig. 1 (waterfall) is gone. Old Fig. 2 to 8 are now 1 to 7; old Fig. 9 (queue contention) is now Fig. 8; old Fig. 10 to 12 are now 9 to 11.

## Still open (not fixed in V3)
- Figs. 9 to 11 (Jakes, RAT pie charts, training convergence) are the original, clipped images.
- The simulator-mode wording ("corrected physics" = mode `baseline_recreation` plus three bug fixes) has not been checked in the text.
- Evidence from the recalculation track (`MA_ROPE_Grok`) is not in any version. In particular, with exploration switched off the paper-reward policy makes no offload attempts; the reported OTR comes from evaluation exploration.
- Nothing is committed to git.

## How versions were checked
`pdftotext` on each PDF, then a search for the phrases above in V1, V2 and V3; page counts from `pdfinfo`. The build for every version is reproducible with `release.sh`, which writes a stamped `.tex` and `.pdf` pair into this folder and moves the previous pair to `releases_archive/`.
