# Task for AG: read-only code-truth check (3 manuscript conflicts)
Repo root: /Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation
Code: src/maro_pe/ (env/config.py, env/channel.py, env/*, training/agent code), scripts/. Manuscript: MA_ROPE_TVT_LATEX_v24_PureSim/sections/*.tex

READ-ONLY. Do NOT edit the manuscript, tables, figures, results or any code. Do NOT run long training. Static reading and small, quick checks only.
Never guess: every answer needs file:line evidence (or a quick command + its output) and a stated confidence.

Question 1 - Reward actually used in training.
 Manuscript says two different things: Methodology IV.A eq (6) r_t = w1*OTR - w2*(max(L-Dmax,0))^2 - w3*E with w=(0.6,0.3,0.1); Algorithm 2 line 7 and Section III say r_t = U (eq 4), U_PRR is the training signal, U_OTR is evaluation only.
 Find the reward function the D3QN/FedAvg training loop really uses (and the one the final evaluation reports). Give the exact formula, weights, and file:line. Say which manuscript statement is correct, or whether both are wrong.

Question 2 - Offload-ratio levels and action count.
 V.A says "6 offload ratio levels from 0.0 to 1.0", |A|=24 theoretical, 11 implemented. Elsewhere rho in {0.25,0.5,0.75,1.0} (4 levels, plus rho=0 local). Table XII uses n_rho=4.
 Report the true set of rho values and the exact 11-entry ACTION_MAP (RAT, rho) from config. State which manuscript sentence is right and what the theoretical |A| should be.

Question 3 - Observation vector and queue discretization.
 Manuscript V.A: 12-dim state [SINR x4, PRR x4, Q, D, L, B] (continuous). IV.D.4 says "queue length discretized to 8 levels".
 Report the real observation vector (dimension, each element, scaling/normalization, whether Q is discretized and to how many levels, whether channel state is quantized). Confirm or refute the 12-dim description and the 8-level sentence.

Extra, only if quick: which commit/campaign directory under results/ produced the numbers in manuscript Table VIII (fleet OTR 0.8274 MA-ROPE, 0.1230 AllOffload at N=32). Previous scan found NO CSV under results/ reproducing them; list your best candidate(s) or say none.

Deliverable: outbox/AG_CODE_TRUTH_REPORT.md in this job folder, with for each question: Answer, Evidence (file:line), Which manuscript text to change (quote it), Confidence, Uncertainty. Also copy it to MA_ROPE_TVT_LATEX_v24_PureSim/handoff_reports/. Record vendor/name. Append a line to events.jsonl. Do not mark the job complete; a verification pass follows.
