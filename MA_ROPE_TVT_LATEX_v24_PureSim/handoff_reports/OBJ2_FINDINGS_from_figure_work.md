# Objective 2 findings discovered while redrawing figures (2026-10-06, Claude Sonnet 5.5)
Not acted on; for the later numbers/provenance pass.

1. Figs 5-6 (speed sweep): the old images match results/speed_sweep_corrected/speed_sweep_results.csv exactly. Redrawn from it (make_figures.py).
2. Figs 7-9 (fleet sweep): the old images match results/CAMPAIGN_CORRECTED_20260803/CORRECTED_BASELINE_RESULTS.csv
   (e.g. MA-ROPE fleet OTR 0.933/0.933/0.888; AllOffload 0.340/0.265/0.125; per-attempt failure MA-ROPE 5.99/4.69/5.46 %).
   The paper TEXT/TABLES quote different values (MA-ROPE 0.849/0.861/0.827; per-attempt 6.20 % vs 3.57 % at N=32; U_OTR 0.521).
   (CORRECTED 2026-10-08: the text numbers DO reproduce from _claude_workspace/results/CAMPAIGN_PHYSICS_FIX_20260818; my first scan missed that folder.) Figures 7-9 plot the older 20260803 campaign, so figures and text still come from different runs.
   Closest others: results/ns3_eval_baselines (MA-ROPE N=8/16/32 = 0.865/0.838/0.809), results/physically_corrected (0.853 / 0.800 at N=8/32).
3. Figs 10-13 images are clipped at the source (also in the old .docx files) and no generating script/data was found:
   Fig 10 queue contention, Fig 11 Jakes SINR vs speed, Fig 12 RAT-selection pies, Fig 13 training convergence.
   Fig 11 shows flat SINR for all RATs, contradicting its caption ("cellular SINR degrades with speed"); it looks like the pre-fix
   Jakes GHz-vs-Hz bug (src/maro_pe/env/channel.py docstring, fix dated 2026-08-18). Needs regeneration from the corrected simulator or removal.
   Even with the fix, the model's fading penalty saturates above ~19 km/h for LTE, so "gradual degradation" would not appear in 20-60 km/h.
4. Baselines jing2019, yun2022, shao2025, xiong2021 not findable as real papers.

## 2026-10-08 additions (figure/title pass)
- Old Fig 1 (literature gap matrix, figures/image1.png, Aug 20 raster) removed: uncited, duplicated Table I, had overlapping header/row. It disagreed with Table I
  (Guo queue: x vs "Per-node"; Yacheur multi-RAT: ~ vs "ITS+LTE") and said Jing 2019 has no partial offload while related_work.tex says Jing models task splitting. Table I kept.
- Repeated CONTENT left for author decision: latency equations (III.D eq 3a/3b vs IV.F.5 eq 10); state vector (IV.C.1 eq 6 vs V.A eq 11);
  DRR defined twice (eq 9 and eq 15); task model twice (III.C and IV.B); III vs IV overlap.
- Figs 2,3,4 are now vector (TikZ / make_figures.py). Fig 2 values = labels printed on the old image. Fig 11 still the clipped pre-fix raster.

## 2026-10-08 duplicate-content removal (done)
Removed: Methodology IV.A "Problem Statement" and IV.B "Task Partitioning Model" (restated III.A/III.C; partition equation moved into III.C);
IV.C State/Action/Reward -> only "Reward Function" remains (state+action now only in V.A "State and Action Space", with the action-space detail merged in);
IV.F.5 latency equation replaced by a pointer to the III.D latency model; results VI.F second DRR definition (old eq 15) replaced by a pointer to eq (7);
stale hard-coded "Section V"/"Table 6" -> \Cref (Results is Section VI).
Kept the 12-dim SINR/PRR state (matches Fig 3, Table XIII, Algorithm 2); the deleted IV.C state was (n_m, q, h_m) discrete counts.
Inconsistencies now exposed, NOT changed (claims/technical):
 - Reward: IV.A eq (6) r_t = w1*OTR - w2*(max(L-D,0))^2 - w3*E (weights .6/.3/.1) vs Algorithm 2 line 7 "r_t = U (Eq 4)" and text saying U_PRR is the training signal.
 - "6 offload ratio levels" (V.A, |A|=24) vs rho in {0.25,0.5,0.75,1} elsewhere (Table XII n_rho=4).
 - IV.D.4 "queue length discretized to 8 levels" vs continuous Q in the 12-dim state.
