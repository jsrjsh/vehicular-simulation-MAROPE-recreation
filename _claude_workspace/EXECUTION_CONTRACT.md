# MA-ROPE Canonical Campaign — Execution Contract

This is the handoff spec for whoever runs the remaining MA-ROPE training (Antigravity or Vivek's
local machine). Follow it exactly — do not improvise on config, seeds, or file locations. When
it's done, hand the output back and I (Claude) will validate it against the pass/fail criteria at
the bottom before anything gets used in the manuscript.

## 1. Why this handoff exists

This sandbox caps every shell command at ~45 seconds with no persistent background processes.
Measured directly on this hardware: MA-ROPE training costs ~18.4s/episode at N=8, ~25.8s/episode
at N=16, and **>42s for a single episode at N=32** (100 episodes/seed are required). N=32 cannot
make any progress at all under a 45-second cap. Rather than keep fighting the sandbox, the
remaining execution moves to unconstrained hardware. Nothing about the protocol changes.

## 2. Exact code to use

Copy these three directories verbatim from this repository's
`01_Engineering/vehicular-simulation-MAROPE-recreation/_claude_workspace/`:

```
_claude_workspace/env/
_claude_workspace/agents/
_claude_workspace/scripts/
```

**Do not edit any file inside `env/` or `agents/`, or `scripts/reproduce_paper_sweeps.py`.** These
are the frozen protocol. `scripts/run_canonical_campaign.py` and
`scripts/generate_canonical_reports.py` are new orchestration files (not part of the frozen
protocol, but also not to be modified — they've been fidelity-verified, see §5).

Before running anything, verify the code hasn't drifted from what was verified here. Compute
sha256 of each of these files and compare against `per_file_hashes` in
`results/CAMPAIGN_CANONICAL_20260802/manifest_partial.json`:

```
env/environment.py, env/config.py, env/channel.py
agents/d3qn/agent.py, agents/d3qn/network.py, agents/d3qn/replay.py
agents/federated/coordinator.py, agents/federated/fedavg.py
agents/privacy/gaussian_ldp.py
scripts/reproduce_paper_sweeps.py
```

If any hash doesn't match, stop and flag it — do not proceed on unverified code.

## 3. Exact command

Run from the repository root (`01_Engineering/vehicular-simulation-MAROPE-recreation/`), with
`env/`, `agents/`, `scripts/` importable via `PYTHONPATH=./_claude_workspace`:

```bash
cd 01_Engineering/vehicular-simulation-MAROPE-recreation
PYTHONPATH=./_claude_workspace python3 _claude_workspace/scripts/run_canonical_campaign.py \
  --campaign-id CAMPAIGN_CANONICAL_20260802 \
  --densities 8,16,32 \
  --seeds 0,1,2,3,4 \
  --budget-seconds 999999
```

**Use the exact campaign ID `CAMPAIGN_CANONICAL_20260802` — do not start a new one.** This resumes
the campaign already in progress: 30/45 combinations (all AllOffload/NoOffload) are already
genuinely complete, and `ma-rope_n8_seed0` has 2/100 episodes of real, checkpointed training
already done. The script is idempotent — it reads `results/CAMPAIGN_CANONICAL_20260802/manifest_partial.json`,
skips anything already marked `"status": "complete"`, and resumes any in-progress MA-ROPE run from
its saved checkpoint in `results/CAMPAIGN_CANONICAL_20260802/_resume_state/`. `--budget-seconds
999999` disables chunking (unnecessary without the 45s cap) — each combo will just run to
completion in one pass.

Expect ~14 more MA-ROPE runs (all densities/seeds except `ma-rope_n8_seed0`, which needs 98 more
episodes). Rough wall-clock budget based on measured per-episode costs: N=8 ≈31 min/seed, N=16
≈43 min/seed, N=32 unmeasured here but expect it to be roughly 2x N=16 by parameter-count scaling
— budget several hours total, more on slower hardware.

After the run completes (or at any checkpoint if you want an interim readout), regenerate the
three deliverable files:

```bash
PYTHONPATH=./_claude_workspace python3 _claude_workspace/scripts/generate_canonical_reports.py \
  results/CAMPAIGN_CANONICAL_20260802
```

This is safe to run at any point — it only reads the manifest, never re-executes training, and
never fabricates rows for incomplete combinations.

## 4. Configuration (frozen, do not tune)

- Environment: `env/environment.py:V2XEnv`, `env_mode="baseline_recreation"`
- Methods: `ma-rope` (trained), `alloffload`, `nooffload` (static policies, already complete)
- Densities: N = 8, 16, 32
- Seeds: 0, 1, 2, 3, 4
- Training: 100 episodes/seed, 100 steps/episode, FedAvg sync every 50 steps, PER replay
  (capacity 5000, batch size 32), target network update every 100 learn() calls, participation
  probability 0.9 — all exactly as in `train_ma_rope()`
- Evaluation: 5 episodes per trained/static policy, exactly as in `evaluate_policy()`
- Orchestrator-only fix (not a protocol change): `torch.manual_seed(seed)` is called before
  constructing each agent/coordinator. The original `train_ma_rope()` never seeds torch's global
  RNG, so network initialization was never actually reproducible run-to-run — this was verified
  empirically (three fresh-process network constructions produced three different first-weight
  values) and is documented in the manifest. No environment, algorithm, or metric formula changed.
- Wu2021: **not included.** No implementation exists anywhere in the recovered codebase (verified
  via exhaustive grep). Do not add one for this campaign — that would be a scope change requiring
  its own review, not a routine execution detail.

## 5. Why this is trustworthy (already verified here, do not re-verify from scratch)

The checkpoint/resume mechanism was proven bit-identical to an uninterrupted call of the real,
frozen `train_ma_rope()`: a manually chunked 1-episode + save/reload + 1-episode run reaches the
exact same checkpoint hash, step count, and FedAvg round count as an uninterrupted 2-episode call
given the same seed (`python3 scripts/run_canonical_campaign.py --verify-fidelity`, which you can
rerun yourself if you want independent confirmation before trusting the resumed run).

## 6. Expected output layout

```
results/CAMPAIGN_CANONICAL_20260802/
  manifest_partial.json                  <- source of truth, updated after every combo
  raw/
    n8/  {ma-rope,alloffload,nooffload}_seed{0-4}.csv, ma-rope_seed{0-4}.pt
    n16/ same pattern
    n32/ same pattern
  _resume_state/                          <- internal chunk checkpoints, not a result
  CANONICAL_CAMPAIGN_MANIFEST.json        <- generated by generate_canonical_reports.py
  CANONICAL_BASELINE_RESULTS.csv          <- generated
  CANONICAL_BASELINE_REPORT.md            <- generated
```

Exactly one CSV (and, for ma-rope, one .pt) per (method, N, seed) combination — 45 combinations
total. The runner aborts with a hard error if it would overwrite a destination file not already
marked complete in the manifest — it will not silently clobber anything.

## 7. Expected CSV schema

`CANONICAL_BASELINE_RESULTS.csv` columns:

```
method, n_agents, seed, checkpoint_hash, run_duration_s,
u_prr_active, u_otr_active, fleet_otr, prr, queue_loss, energy_active, latency_active,
source_file
```

Per-combo raw CSVs (`raw/n{N}/{method}_seed{S}.csv`) use `evaluate_policy()`'s native schema:
`env_mode, policy_type, seed, episode, u_prr_step, u_prr_active, u_otr_step, u_otr_active,
fleet_otr, prr, latency_active_ms, latency_step_ms, energy_active_j, energy_step_j, queue_loss,
checkpoint_hash` — 5 rows (one per eval episode) per file.

## 8. Figures

None required for this campaign. This is the raw baseline result set (mission Phase 3), not the
final paper figures (Phase 7/8). Do not generate plots against these numbers yet — they haven't
been reviewed.

## 9. Validation checks I will run on the returned output (pass/fail)

- [ ] `CANONICAL_CAMPAIGN_MANIFEST.json` shows all 45 combinations with `"status": "complete"` —
      zero `"in_progress"`, zero missing.
- [ ] `CANONICAL_BASELINE_RESULTS.csv` has exactly 45 data rows (46 with header).
- [ ] Every row's `checkpoint_hash` for `ma-rope` is non-empty and a real file
      `raw/n{N}/ma-rope_seed{S}.pt` exists whose filename-embedded hash matches
      `get_checkpoint_hash()` recomputed from its actual contents.
- [ ] `nooffload` rows have `queue_loss == 0.0` for every seed/density (no offloading occurs, so
      nothing can be queue-dropped — this is a structural invariant, not a soft check).
- [ ] `alloffload` rows show `mean_rho`/action distribution consistent with `rho=1.0` always
      taken when offloading (per the frozen policy logic) — spot-checked from the raw CSVs.
- [ ] `per_file_hashes` in the final manifest still match §2's recomputed hashes — proves no code
      drift occurred mid-campaign.
- [ ] `code_hash_sha256` is identical across every run in the manifest (all 45 entries reflect the
      same frozen code, not a mix of versions).
- [ ] No `V2XEnvPlus` or `train_b3_baselines.py` references appear anywhere in the manifest or
      generated report.
- [ ] `wu2021_status` field explicitly states exclusion — not silently absent.
- [ ] Spot-check: rerun `--verify-fidelity` on the receiving machine before trusting its output,
      confirm it also reports `PASS`.

If all of these pass, the result set is accepted as the canonical baseline and I resume Phase 4
(root-cause analysis against these real numbers) and Phase 6 (path selection). If any fail, work
stops there and gets reported rather than patched over.
