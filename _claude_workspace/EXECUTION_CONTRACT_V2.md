# MA-ROPE Corrected Campaign (Path B) — Execution Contract V2

Handoff spec for whoever runs the fresh, uncontaminated Path B campaign (Antigravity or Vivek's
local machine) — item 6 of the correction plan ("run a fresh uncontaminated five-seed campaign").
Follow it exactly. This is a **new campaign, not a resume of `CAMPAIGN_CANONICAL_20260802`** —
Path A's results stay untouched as the historical record; this produces a separate, independently
named result set.

## 1. Why this exists

Per `QUEUE_LOSS_ROOT_CAUSE_REPORT.md`'s verdict ("4. MIXED CAUSES" — denominator choice interacting
with per-RAT reliability, plus an independently-discovered checkpoint-persistence gap), the
following corrections were made and locally fidelity-verified in this sandbox:

1. Metric renamed: `queue_loss` → `conditional_tx_failure_rate` (identical computation — failures
   / attempted transmissions only — only the name changed, so it stops implying a queue-capacity
   drop mechanism that doesn't exist in the code).
2. Two new metrics added: `fleet_tx_failure_rate` (failures / ALL vehicle-steps, the denominator
   that does not reverse the MA-ROPE-vs-AllOffload ordering) and absolute counts
   (`fleet_tx_failure_count_total`, `fleet_tx_attempt_count_total`, `total_vehicle_steps_total`).
3. Checkpoint persistence fixed: the final `.pt` now saves **all N agents'** `online_net`
   state_dicts (`all_agent_online_net_state_dicts`), not just agent 0's — closing the gap where
   `evaluate_policy()` evaluates every agent's individually-trained weights but only one agent's
   weights survived to disk.

Nothing else changed: same `env/environment.py:V2XEnv`, same `env_mode="baseline_recreation"`,
same D3QN+PER+FedAvg algorithm and hyperparameters, same other metrics (U_PRR, U_OTR, fleet_otr,
energy, latency). This sandbox still caps every shell command at ~45 seconds with no persistent
background processes, so — as with Path A — execution moves to unconstrained hardware; my role
is to define/verify the protocol here and validate the returned output afterward.

## 2. Exact code to use

Copy these three directories verbatim from
`01_Engineering/vehicular-simulation-MAROPE-recreation/_claude_workspace/`:

```
_claude_workspace/env/
_claude_workspace/agents/
_claude_workspace/scripts/
```

**Do not edit any file inside `env/` or `agents/`, or `scripts/reproduce_paper_sweeps.py`** — these
are still the frozen protocol, byte-for-byte unchanged from Path A. `scripts/run_corrected_campaign.py`
and `scripts/generate_corrected_reports.py` are the new Path B orchestration files — do not modify
them either; they've been fidelity-verified (see §5).

Before running anything, verify the code hasn't drifted. Compute sha256 of each of these and
compare against `per_file_hashes` in the fresh campaign's `manifest_partial.json` once created (or
against `results/CAMPAIGN_CANONICAL_20260802/manifest_partial.json`'s `per_file_hashes` — they must
be identical, since none of these files changed for Path B):

```
env/environment.py, env/config.py, env/channel.py
agents/d3qn/agent.py, agents/d3qn/network.py, agents/d3qn/replay.py
agents/federated/coordinator.py, agents/federated/fedavg.py
agents/privacy/gaussian_ldp.py, scripts/reproduce_paper_sweeps.py
```

If any hash doesn't match either reference, stop and flag it — do not proceed on unverified code.

## 3. Exact command

```bash
cd 01_Engineering/vehicular-simulation-MAROPE-recreation
PYTHONPATH=./_claude_workspace python3 _claude_workspace/scripts/run_corrected_campaign.py \
  --campaign-id CAMPAIGN_CORRECTED_20260803 \
  --densities 8,16,32 \
  --seeds 0,1,2,3,4 \
  --budget-seconds 999999
```

**Use the exact campaign ID `CAMPAIGN_CORRECTED_20260803`** (or whatever fresh ID you actually
start it under — just record it and use it consistently; do not silently rename mid-campaign). This
is a brand-new campaign — no prior partial progress to resume. The script is idempotent: if a call
is interrupted, rerunning the identical command resumes from `manifest_partial.json` and each
in-progress MA-ROPE run's own checkpoint in `results/CAMPAIGN_CORRECTED_20260803/_resume_state/`.
`--budget-seconds 999999` disables chunking (unnecessary without the 45s cap).

Expect all 45 combinations to run fresh. Rough wall-clock budget, based on Path A's measured
per-episode costs (unchanged algorithm, so should transfer directly): N=8 ≈31 min/seed, N=16
≈43 min/seed, N=32 was measured at >42s/episode in-sandbox and took roughly 2x N=16 per-episode on
the unconstrained hardware that ran Path A (see `CAMPAIGN_CANONICAL_20260802/manifest_partial.json`
for exact recorded durations) — budget several hours total across all 15 MA-ROPE combos, more on
slower hardware. The 30 static-policy combos (AllOffload/NoOffload) are cheap (~1-2s each).

After the run completes (or at any checkpoint, for an interim readout), regenerate the three Path B
deliverables:

```bash
PYTHONPATH=./_claude_workspace python3 _claude_workspace/scripts/generate_corrected_reports.py \
  results/CAMPAIGN_CORRECTED_20260803
```

Safe to run at any point — only reads the manifest, never re-executes training, never fabricates
rows for incomplete combos. (Smoke-tested against a synthetic manifest in this sandbox before being
included in this contract — see CLAUDE_FINDINGS.md.)

## 4. Configuration (frozen, do not tune)

Identical to Path A's §4 in every respect except output naming and the two metric/checkpoint
changes described in §1:

- Environment: `env/environment.py:V2XEnv`, `env_mode="baseline_recreation"`
- Methods: `ma-rope` (trained), `alloffload`, `nooffload` (static)
- Densities: N = 8, 16, 32. Seeds: 0, 1, 2, 3, 4.
- Training: 100 episodes/seed, 100 steps/episode, FedAvg sync every 50 steps, PER replay (capacity
  5000, batch size 32), target network update every 100 `learn()` calls, participation probability
  0.9 — exactly as `train_ma_rope()`.
- Evaluation: 5 episodes per policy, exactly as `evaluate_policy()`'s logic (reimplemented as
  `evaluate_policy_v2()` — identical physics/math, only output schema differs, see §7).
- `torch.manual_seed(seed)` called before each agent/coordinator construction — same orchestrator-
  only fix as Path A, not a protocol change (documented in the manifest).
- Wu2021: **not included** (no implementation exists anywhere in the codebase — verified by
  exhaustive grep, same finding as Path A).

## 5. Why this is trustworthy (already verified here, do not re-verify from scratch)

Two independent checks were run in this sandbox before this contract was written
(`python3 scripts/run_corrected_campaign.py --verify-fidelity`, rerun it yourself for independent
confirmation before trusting the campaign):

1. **Chunk-resume fidelity** (inherited unchanged from Path A): a manually chunked 1-episode +
   save/reload + 1-episode run reaches the identical checkpoint hash, step count, and FedAvg round
   count as an uninterrupted 2-episode call of the real `train_ma_rope()`, given the same seed.
   Result: `PASS — bit-identical`.
2. **All-agent checkpoint persistence** (the new Path B capability): trained a small fixture
   (`n_agents=3`, 2 real episodes, confirmed `update_count > 0` so the check isn't trivially
   passing on an untrained network), then verified the final `.pt`'s
   `all_agent_online_net_state_dicts` contains exactly `n_agents` entries and each entry is
   byte-identical (`torch.equal` per tensor) to that same agent's live in-memory weights at save
   time. Result: `PASS`.

Both checks exited 0 (`OVERALL: chunk-resume fidelity=PASS, all-agent checkpoint
persistence=PASS`).

## 6. Expected output layout

```
results/CAMPAIGN_CORRECTED_20260803/
  manifest_partial.json                  <- source of truth, updated after every combo
  raw/
    n8/  {ma-rope,alloffload,nooffload}_seed{0-4}.csv, ma-rope_seed{0-4}.pt
    n16/ same pattern
    n32/ same pattern
  _resume_state/                          <- internal chunk checkpoints, not a result
  CORRECTED_CAMPAIGN_MANIFEST.json        <- generated by generate_corrected_reports.py
  CORRECTED_BASELINE_RESULTS.csv          <- generated
  CORRECTED_BASELINE_REPORT.md            <- generated
```

Exactly one CSV (and, for ma-rope, one `.pt`) per (method, N, seed) — 45 combinations total. The
runner aborts with a hard error if it would overwrite a destination not already marked complete in
the manifest.

**Do not write anything to `results/paper_reproduction/` or `results/CAMPAIGN_CANONICAL_20260802/`**
— those are Path A's, untouched. Intermediate per-episode staging lands in
`results/corrected_v2_staging/`, distinct from Path A's `results/paper_reproduction/`, before being
copied into this campaign's `raw/` — this is internal to the script, no action needed, just don't
be alarmed to see that directory appear.

## 7. Expected CSV schema

`CORRECTED_BASELINE_RESULTS.csv` columns:

```
method, n_agents, seed, checkpoint_hash, run_duration_s,
u_prr_active, u_otr_active, fleet_otr, prr,
conditional_tx_failure_rate, fleet_tx_failure_rate,
fleet_tx_failure_count_total, fleet_tx_attempt_count_total, total_vehicle_steps_total,
energy_active, latency_active,
source_file
```

Per-combo raw CSVs (`raw/n{N}/{method}_seed{S}.csv`) use `evaluate_policy_v2()`'s native schema:

```
env_mode, policy_type, seed, episode,
u_prr_step, u_prr_active, u_otr_step, u_otr_active,
fleet_otr, prr, latency_active_ms, latency_step_ms, energy_active_j, energy_step_j,
conditional_tx_failure_rate, fleet_tx_failure_rate,
fleet_tx_failure_count, fleet_tx_attempt_count, total_vehicle_steps,
checkpoint_hash
```

— 5 rows (one per eval episode) per file. Note `queue_loss` does **not** appear anywhere in this
campaign's output; any script or figure that still reads that column name needs updating before it
can consume this campaign's data (this is intentional — the manuscript-impact memo, task #50,
covers exactly what downstream needs updating).

## 8. Figures

None required for this campaign. This is the corrected raw baseline result set. Do not generate
plots against these numbers until they've passed §9 and the manuscript-impact memo has assessed
what, if anything, changes in the paper.

## 9. Validation checks I will run on the returned output (pass/fail)

- [ ] `CORRECTED_CAMPAIGN_MANIFEST.json` shows all 45 combinations `"status": "complete"` — zero
      `"in_progress"`, zero missing.
- [ ] `CORRECTED_BASELINE_RESULTS.csv` has exactly 45 data rows (46 with header).
- [ ] Every `ma-rope` row's `checkpoint_hash` is non-empty and `raw/n{N}/ma-rope_seed{S}.pt` exists;
      `get_checkpoint_hash()` recomputed from the file's `all_agent_online_net_state_dicts[0]`
      matches the filename-embedded hash.
- [ ] **New check specific to Path B**: for every `ma-rope` `.pt` file,
      `len(torch.load(path)["all_agent_online_net_state_dicts"]) == n_agents` for that combo's N —
      confirms the checkpoint fix actually shipped in the real campaign output, not just the small
      fixture used in §5.
- [ ] `nooffload` rows have `conditional_tx_failure_rate == 0.0` for every seed/density (structural
      invariant, unchanged from Path A: no offload attempted, so nothing can fail a transmission it
      never attempted).
- [ ] `fleet_tx_attempt_count_total + (steps where no offload attempted) == total_vehicle_steps_total`
      for every row — sanity-checks the two new denominators are internally consistent.
- [ ] `per_file_hashes` in the final manifest match §2's recomputed hashes — no code drift mid-run.
- [ ] `code_hash_sha256` identical across all 45 entries.
- [ ] No `V2XEnvPlus` or `train_b3_baselines.py` references anywhere in the manifest or report.
- [ ] `wu2021_status` explicitly states exclusion.
- [ ] Spot-check: rerun `--verify-fidelity` on the receiving machine before trusting its output,
      confirm `OVERALL: ... PASS, ... PASS`.
- [ ] Cross-check against Path A: for `alloffload`/`nooffload` rows, `conditional_tx_failure_rate`
      here should match `queue_loss` in `CAMPAIGN_CANONICAL_20260802/CANONICAL_BASELINE_RESULTS.csv`
      for the same (N, seed) — these are static policies with no training randomness, so the two
      campaigns should agree exactly (or reveal an environment/code drift if they don't).

If all of these pass, the result set is accepted as the corrected baseline and I proceed to the
manuscript-impact memo (task #50) and, per the user's standing instruction, do not send any
manuscript version to the professor until that memo is reviewed. If any fail, work stops there and
gets reported rather than patched over.
