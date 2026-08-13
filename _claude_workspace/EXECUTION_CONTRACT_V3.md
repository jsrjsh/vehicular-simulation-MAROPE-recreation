# MA-ROPE Corrected Campaign + Training-Duration Diagnostic — Execution Contract V3

Supersedes `EXECUTION_CONTRACT_V2.md` for the corrected campaign (adds one new baseline — see §2)
and adds a second, separate deliverable (the training-duration diagnostic — see §3). Both run on
unconstrained hardware (Antigravity/local machine), per the standing instruction that expensive
execution happens off-sandbox and my role is to specify, fidelity-verify, and validate afterward.

## 0. What changed since V2, and why

Per the correction plan's item 2 ("implement at least one real non-trivial baseline"), the
manuscript's only other named comparator besides AllOffload/NoOffload — Wu2021 — was investigated
for feasibility:

- The manuscript cites Wu2021 (`references.bib`: Y. Wu, F. Liu, Z. Chen, "UCB-based task offloading
  for vehicular edge computing," IEEE IoT-J) but provides **no equations, pseudocode, or
  hyperparameters anywhere in the manuscript** — only a one-line gloss ("4-arm stateless bandit,"
  `experiments.tex`) and a feature table (`related_work.tex` Table I) marking Wu2021 as
  Multi-RAT=NO, Partial-ρ=NO, FL-Privacy=NO. A faithful, certifiable reproduction is not possible
  from what's recovered.
- **New finding, not previously documented**: the manuscript's Experimental Setup (`experiments.tex`
  line 16) actually names **five** comparator baselines with no recovered implementation — MADDPG,
  CoopEC-Shao2025, UCB-Wu2021, Lyapunov-Jing2019, GA+DQN-Yun2022 — each described in one clause with
  no algorithmic detail. This is a materially larger gap than the single "Wu2021" item previously
  scoped in `PUBLICATION_DECISION.md` Tier 1, item 4, and should be treated as its own open item
  when that document is next revisited. Not resolved here — implementing all five is out of scope
  for this contract; only the one instructed by the correction plan is addressed below.
- **Decision**: implemented a disclosed, clearly-labeled **reconstruction**, not a certified
  reproduction — a stateless UCB1 bandit over 4 arms consistent with Wu2021's own feature-table
  properties (single RAT, no partial ρ, no cross-vehicle coordination): `{Local, 5G-NR@25%,
  5G-NR@50%, 5G-NR@100%}` (`ACTION_MAP` entries 0, 6, 7, 8). Every artifact this produces must be
  labeled **"UCB-RAT (Wu2021-inspired reconstruction)"** — never "Wu2021" unqualified — in any
  table, figure, or manuscript text. See `scripts/run_corrected_campaign.py`'s `UCB_ARMS` constant
  and its adjacent comment block for the full reconstruction rationale.
- Also built, per correction-plan item 3: `scripts/run_training_duration_diagnostic.py`, a separate
  script answering whether MA-ROPE's WiFi6 over-reliance is a converged tradeoff or a training-
  duration artifact (§3).

Both additions were smoke-tested in this sandbox before being included in this contract (small
fixture runs, not the real campaign — see `CLAUDE_FINDINGS.md`).

---

## 1. Exact code to use

Same as `EXECUTION_CONTRACT_V2.md` §2 — `env/`, `agents/`, verify hashes against
`per_file_hashes` in `CAMPAIGN_CANONICAL_20260802/manifest_partial.json` before running anything.
`scripts/reproduce_paper_sweeps.py` remains untouched. `scripts/run_corrected_campaign.py`,
`scripts/generate_corrected_reports.py`, and the new `scripts/run_training_duration_diagnostic.py`
are the orchestration files for this contract — do not modify them.

## 2. Deliverable A — corrected canonical campaign (now 4 methods, not 3)

```bash
cd 01_Engineering/vehicular-simulation-MAROPE-recreation
PYTHONPATH=./_claude_workspace python3 _claude_workspace/scripts/run_corrected_campaign.py \
  --campaign-id CAMPAIGN_CORRECTED_20260803 \
  --densities 8,16,32 \
  --seeds 0,1,2,3,4 \
  --budget-seconds 999999
```

Unchanged from V2 in every other respect (config, checkpoint policy, output layout, metric
schema — see `EXECUTION_CONTRACT_V2.md` §4/§6/§7). The only difference: `run_corrected_campaign.py`
now runs **4 methods** by default (`alloffload`, `nooffload`, `ucb_bandit`, `ma-rope`), so this is
now a **60-combination campaign** (4 × 3 densities × 5 seeds), not 45. `ucb_bandit` is a static
policy in the engineering sense (no separate pretraining phase — it learns online during its own 5
evaluation episodes, persisted across those episodes, never reset mid-run) and costs about the same
as AllOffload/NoOffload to execute (~1-2s per combo).

After completion:

```bash
PYTHONPATH=./_claude_workspace python3 _claude_workspace/scripts/generate_corrected_reports.py \
  results/CAMPAIGN_CORRECTED_20260803
```

**Validation checklist**: `EXECUTION_CONTRACT_V2.md` §9, items 1-2 updated to expect 60 combinations
(61 with header) instead of 45, plus one new check:

- [ ] Every `ucb_bandit` row's action distribution (recoverable by re-running
      `evaluate_policy_v2(..., track_actions=True)` against the same seed) uses only actions
      `{0, 6, 7, 8}` — confirms the bandit never selected an action outside its declared 4-arm set.

## 3. Deliverable B — training-duration diagnostic (separate from Deliverable A, do not mix outputs)

```bash
cd 01_Engineering/vehicular-simulation-MAROPE-recreation
PYTHONPATH=./_claude_workspace python3 _claude_workspace/scripts/run_training_duration_diagnostic.py \
  --diagnostic-id CAMPAIGN_TRAINING_DURATION_20260803 \
  --n-agents 32 --seed 0 \
  --checkpoints 100,250,500 \
  --budget-seconds 999999
```

**Single seed by design** (N=32, seed=0 — the density/seed most directly relevant to the queue-loss
investigation this follows up on). Do not expand to additional seeds without first reviewing
whether this seed's trajectory materially changes across the three checkpoints — that review is a
judgment call for the scientist evaluating the output, not something the script or its executor
should decide unilaterally. If AG or whoever runs this believes the trend clearly warrants
expansion, flag it back rather than silently expanding scope.

This trains MA-ROPE sequentially to 100, then 250, then 500 episodes (resuming from its own
checkpoint each time — the standard chunked mechanism, fidelity-verified for the underlying
save/resume primitives in the Path B work), evaluating at each stopping point with the standard
5-episode protocol plus action/RAT-distribution tracking. Its checkpoint/resume state
(`results/CAMPAIGN_TRAINING_DURATION_20260803/_resume_state/`) is entirely separate from
Deliverable A's — running both does not interfere with either.

Automatically produces `TRAINING_DURATION_RESULTS.csv`, `manifest.json`, and `EXECUTION_REPORT.md`
(the last one is data-only — raw trajectory table, no interpretation, per the standing instruction
not to interpret the science during execution).

**Validation checklist**:

- [ ] `TRAINING_DURATION_RESULTS.csv` has exactly 3 rows (100/250/500), each `status: complete` in
      the manifest.
- [ ] `step_count` values are exactly 10x the episode count (100 steps/episode) — 10000/25000/50000.
- [ ] `checkpoint_hash` differs across all three rows (proves each checkpoint reflects genuinely
      different, further-trained weights, not a stale/reused checkpoint).
- [ ] The three `.pt` files in `raw/` are each a full `all_agent_online_net_state_dicts` payload
      with exactly 32 entries (same check as `EXECUTION_CONTRACT_V2.md`'s Path-B-specific item).
- [ ] `rat_usage` and `action_distribution_json` are present and sum to `total_vehicle_steps_total`
      for every row (internal consistency of the tracked distribution).

## 4. What I will NOT do until both deliverables are validated

Per the standing instruction: no manuscript edits, no figure generation, no claim-by-claim impact
list, no GO/NO-GO recommendation. Both deliverables come back to me for scientific validation
first — hash/structural/timing re-verification, exactly as done for `CAMPAIGN_CANONICAL_20260802`
and the AG-executed portion of it. Only after that validation do I produce corrected result tables,
corrected figures, the claim-by-claim manuscript impact list, and a final GO/NO-GO recommendation
for professor review.
