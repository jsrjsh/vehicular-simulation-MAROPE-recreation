# MODE_SEPARATION_REPORT.md

This document verifies the strict directory separation between `baseline_recreation` (paper reproduction) and `physically_corrected` outputs.

---

## 1. Directory Structure Layout
* **Paper Reproduction Directory:** [`results/paper_reproduction/`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/results/paper_reproduction)
* **Physically Corrected Directory:** [`results/physically_corrected/`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/results/physically_corrected)

---

## 2. Manifest Verification

The following evaluation log files and checkpoints have been isolated correctly:

### results/paper_reproduction/n8/
- alloffload_seed_0_ep_5_hash_none.csv
- alloffload_seed_1_ep_5_hash_none.csv
- alloffload_seed_2_ep_5_hash_none.csv
- alloffload_seed_3_ep_5_hash_none.csv
- alloffload_seed_4_ep_5_hash_none.csv
- ma-rope_seed_0_ep_100_hash_126ca59e.pt
- ma-rope_seed_0_ep_5_hash_126ca59e.csv
- ma-rope_seed_0_ep_5_hash_fd045af8.csv
- ma-rope_seed_1_ep_100_hash_02f0816f.pt
- ma-rope_seed_1_ep_5_hash_02f0816f.csv
- ma-rope_seed_1_ep_5_hash_e29128da.csv
- ma-rope_seed_2_ep_100_hash_d6e5a1b9.pt
- ma-rope_seed_2_ep_5_hash_0cb57832.csv
- ma-rope_seed_2_ep_5_hash_d6e5a1b9.csv
- ma-rope_seed_3_ep_100_hash_449b4e48.pt
- ma-rope_seed_3_ep_5_hash_449b4e48.csv
- ma-rope_seed_3_ep_5_hash_711bd38f.csv
- ma-rope_seed_4_ep_100_hash_32bbe738.pt
- ma-rope_seed_4_ep_5_hash_32bbe738.csv
- ma-rope_seed_4_ep_5_hash_e8bc8b12.csv
- nooffload_seed_0_ep_5_hash_none.csv
- nooffload_seed_1_ep_5_hash_none.csv
- nooffload_seed_2_ep_5_hash_none.csv
- nooffload_seed_3_ep_5_hash_none.csv
- nooffload_seed_4_ep_5_hash_none.csv

### results/physically_corrected/n8/
- alloffload_seed_0_ep_5_hash_none.csv
- alloffload_seed_1_ep_5_hash_none.csv
- alloffload_seed_2_ep_5_hash_none.csv
- alloffload_seed_3_ep_5_hash_none.csv
- alloffload_seed_4_ep_5_hash_none.csv
- ma-rope_seed_0_ep_100_hash_82dee9ff.pt
- ma-rope_seed_0_ep_5_hash_3a0e5b39.csv
- ma-rope_seed_0_ep_5_hash_82dee9ff.csv
- ma-rope_seed_1_ep_100_hash_4bc9ce68.pt
- ma-rope_seed_1_ep_5_hash_0c73f63f.csv
- ma-rope_seed_1_ep_5_hash_4bc9ce68.csv
- ma-rope_seed_2_ep_100_hash_08e7d4cb.pt
- ma-rope_seed_2_ep_5_hash_08e7d4cb.csv
- ma-rope_seed_2_ep_5_hash_201d679a.csv
- ma-rope_seed_3_ep_100_hash_cfdb3ab2.pt
- ma-rope_seed_3_ep_5_hash_0e64a85e.csv
- ma-rope_seed_3_ep_5_hash_cfdb3ab2.csv
- ma-rope_seed_4_ep_100_hash_01d784f8.pt
- ma-rope_seed_4_ep_5_hash_01d784f8.csv
- ma-rope_seed_4_ep_5_hash_3040e904.csv
- nooffload_seed_0_ep_5_hash_none.csv
- nooffload_seed_1_ep_5_hash_none.csv
- nooffload_seed_2_ep_5_hash_none.csv
- nooffload_seed_3_ep_5_hash_none.csv
- nooffload_seed_4_ep_5_hash_none.csv

### results/paper_reproduction/n32/
- alloffload_seed_0_ep_5_hash_none.csv
- alloffload_seed_1_ep_5_hash_none.csv
- alloffload_seed_2_ep_5_hash_none.csv
- alloffload_seed_3_ep_5_hash_none.csv
- alloffload_seed_4_ep_5_hash_none.csv
- ma-rope_seed_0_ep_100_hash_7210f354.pt
- ma-rope_seed_0_ep_5_hash_51a568b6.csv
- ma-rope_seed_0_ep_5_hash_7210f354.csv
- ma-rope_seed_1_ep_100_hash_6745023c.pt
- ma-rope_seed_1_ep_5_hash_380e7b05.csv
- ma-rope_seed_1_ep_5_hash_6745023c.csv
- ma-rope_seed_2_ep_100_hash_18fa7e28.pt
- ma-rope_seed_2_ep_5_hash_18fa7e28.csv
- ma-rope_seed_2_ep_5_hash_84e481c5.csv
- ma-rope_seed_3_ep_100_hash_0e806ec8.pt
- ma-rope_seed_3_ep_5_hash_0e806ec8.csv
- ma-rope_seed_3_ep_5_hash_9d4e3a61.csv
- ma-rope_seed_4_ep_100_hash_cff53769.pt
- ma-rope_seed_4_ep_5_hash_cff53769.csv
- ma-rope_seed_4_ep_5_hash_dfc4e990.csv
- nooffload_seed_0_ep_5_hash_none.csv
- nooffload_seed_1_ep_5_hash_none.csv
- nooffload_seed_2_ep_5_hash_none.csv
- nooffload_seed_3_ep_5_hash_none.csv
- nooffload_seed_4_ep_5_hash_none.csv

### results/physically_corrected/n32/
- alloffload_seed_0_ep_5_hash_none.csv
- alloffload_seed_1_ep_5_hash_none.csv
- alloffload_seed_2_ep_5_hash_none.csv
- alloffload_seed_3_ep_5_hash_none.csv
- alloffload_seed_4_ep_5_hash_none.csv
- ma-rope_seed_0_ep_100_hash_d446fbcb.pt
- ma-rope_seed_0_ep_5_hash_775b0aba.csv
- ma-rope_seed_0_ep_5_hash_d446fbcb.csv
- ma-rope_seed_1_ep_100_hash_1deb223e.pt
- ma-rope_seed_1_ep_5_hash_1deb223e.csv
- ma-rope_seed_1_ep_5_hash_6ae2b800.csv
- ma-rope_seed_2_ep_100_hash_c49d137e.pt
- ma-rope_seed_2_ep_5_hash_73b65184.csv
- ma-rope_seed_2_ep_5_hash_c49d137e.csv
- ma-rope_seed_3_ep_100_hash_b96e4f85.pt
- ma-rope_seed_3_ep_5_hash_8427c123.csv
- ma-rope_seed_3_ep_5_hash_b96e4f85.csv
- ma-rope_seed_4_ep_100_hash_ccab4758.pt
- ma-rope_seed_4_ep_5_hash_ac7768a9.csv
- ma-rope_seed_4_ep_5_hash_ccab4758.csv
- nooffload_seed_0_ep_5_hash_none.csv
- nooffload_seed_1_ep_5_hash_none.csv
- nooffload_seed_2_ep_5_hash_none.csv
- nooffload_seed_3_ep_5_hash_none.csv
- nooffload_seed_4_ep_5_hash_none.csv
