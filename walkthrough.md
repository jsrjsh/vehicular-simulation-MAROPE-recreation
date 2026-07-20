# Walkthrough - Phase 4A.2: Controlled Baseline Reproduction

We have successfully completed Phase 4A.2, implementing all metrics semantics corrections, fixed baseline bypass policies, five-seed training sweeps for N=8 and N=32, and isolating output directories.

---

## 1. Accomplishments

* **Metric Semantics Isolation:** Created `METRIC_DEFINITION_SPEC.md` separating `*_per_step` and `*_per_active_task` average metrics to resolve arrival probability dilution.
* **Fixed Baselines Bypass:** Implemented custom bypass in `env/environment.py` and `BASELINE_POLICY_SPEC.md` preventing adaptive SINR-proportional $\rho$ scaling for fixed AllOffload ($\rho=1.0$ locked) and NoOffload ($\rho=0.0$ locked) policies.
* **Five-Seed sweeps:** Executed full 100-episode training sweeps over seeds 0, 1, 2, 3, and 4 under both `baseline_recreation` and `physically_corrected` modes.
* **Isolated Result Directories:** Correctly organized CSV reports and `.pt` model checkpoints into isolated subfolders `results/paper_reproduction/` and `results/physically_corrected/`.
* **Regression Testing:** Added regression tests in `tests/test_reproduction.py` verifying fixed bypass policies, denominator averages, seed aggregation calculations, and isolated folders. All 60 unit tests pass cleanly.

---

## 2. Manifest of New Deliverables

1. [`METRIC_DEFINITION_SPEC.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/METRIC_DEFINITION_SPEC.md): Formula definitions of denominators.
2. [`BASELINE_POLICY_SPEC.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/BASELINE_POLICY_SPEC.md): Bypassing SINR adjustments for fixed baselines.
3. [`TRAINING_PROTOCOL_PARITY.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/TRAINING_PROTOCOL_PARITY.md): Manifest log of the 5-seed training runs.
4. [`N8_REPRODUCTION_REPORT.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/N8_REPRODUCTION_REPORT.md): N=8 paper comparison matrix.
5. [`N32_REPRODUCTION_REPORT.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/N32_REPRODUCTION_REPORT.md): N=32 paper comparison matrix.
6. [`FIVE_SEED_AGGREGATION_REPORT.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/FIVE_SEED_AGGREGATION_REPORT.md): Seed aggregation statistics.
7. [`MODE_SEPARATION_REPORT.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/MODE_SEPARATION_REPORT.md): Verifies result directories isolation.
8. [`PHASE4A2_TEST_REPORT.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/PHASE4A2_TEST_REPORT.md): Logs regression test validation.
9. [`REPRODUCIBILITY_REPORT.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/REPRODUCIBILITY_REPORT.md): Traces final reproducibility matrices.
10. [`PHASE4A2_EXECUTIVE_RESULTS.md`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/PHASE4A2_EXECUTIVE_RESULTS.md): Detailed comparative tables, audit answers, and docx paper root-cause analysis.
11. [`MA_ROPE_IEEE_Paper_v10_final2.docx`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/MA_ROPE_IEEE_Paper_v10_final2.docx): The source manuscript.
12. [`scripts/extract_docx.py`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/scripts/extract_docx.py): Word text parser utility.
13. [`scripts/extracted_paper_text.txt`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/scripts/extracted_paper_text.txt): Plain text extraction of the paper.
14. Checkpoints and CSV outputs logged in `results/`.

---

## 3. Git Versioning

All changes have been successfully committed to Git with the message:
`"Phase 4A.2: controlled manuscript-compatible reproduction"`
