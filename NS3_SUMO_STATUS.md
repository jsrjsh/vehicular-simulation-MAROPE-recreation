# NS3_SUMO_STATUS.md

Status of the SUMO + ns-3 co-simulation integration, on `experiment/city-scale`.
Read this before starting a session on this work, in either Claude or Antigravity --
this file is the single source of truth so the two don't drift out of sync.

## Objective

Replace the deterministic Python `V2XEnv` with a SUMO (mobility) + ns-3 (network
physics) co-simulation, **without regressing performance relative to the validated
Python baseline**. Two Python baselines matter here, don't conflate them:
- `CAMPAIGN_CORRECTED_20260803` -- v25's numbers (MA-ROPE 88.8% fleet OTR / 0.951
  DRR at N=32 vs AllOffload 12.5% / 0.367). This is what's actually in the paper.
- `CAMPAIGN_LATENCY_FIX_20260815` -- a retrain under an isolated one-line fix to
  a log10 latency bug found 2026-08-15 (see below). **This is the correct
  comparison point for the ns-3 work**, since the ns-3 physics port also carries
  that same fix -- comparing ns-3 against v25 directly would conflate two
  different changes.

## Current status: core physics validation is DONE (2026-08-16)

**Headline result: MA-ROPE's Fleet OTR/PRR under real ns-3 physics + real SUMO
mobility matches the Python baseline (`CAMPAIGN_LATENCY_FIX_20260815`) within
~3 percentage points at every density (N=8/16/32).** This is the answer to the
question this whole detour was trying to answer -- yes, the algorithm's
advantage is not an artifact of the analytical Python approximation.

| N | Python Fleet OTR (seeds 0-2) | ns-3 Fleet OTR (seeds 0-2) | Diff |
|---|---|---|---|
| 8 | 0.881 | 0.852 | -2.9pp |
| 16 | 0.835 | 0.843 | +0.7pp |
| 32 | 0.838 | 0.809 | -2.9pp |

Raw per-seed CSVs: `results/ns3_eval_n{8,16,32}_seed{0,1,2}.csv` (repo root,
**not** `_claude_workspace/results/` -- a path-join quirk in
`scripts/ns3_eval_ma_rope.py`, low-priority to fix, not yet done).

### What's actually implemented now

- `src/maro_pe/simulation/channel_model.h` -- C++ channel physics (SINR, path
  loss, Jakes fading, link-success), golden-tested against real Python output
  (2026-08-15), matches to 1e-9.
- `src/maro_pe/simulation/v2x_environment.h` -- `V2XEnvironment`, the full C++
  port of `env/environment.py`'s task generation, RSU queue model, latency
  computation, Bernoulli link success, and the composite utility/reward. Reads
  real node positions/velocities from ns-3's `MobilityModel` (2D, via
  `ns3::CalculateDistance`) -- the old fake 1D `std::fmod` mobility loop is gone.
- `src/maro_pe/simulation/ns3_script.cc` -- wires `V2XEnvironment` into the
  OpenGym callbacks (`MyGetObservation`, `MyExecuteActions`, `BuildExtraInfo`),
  installs `Ns2MobilityHelper` from a SUMO trace when `--traceFile` is passed.
- `src/maro_pe/simulation/sumo_scenario/` -- SUMO net/route/trace files. Road
  is 2600m (`netgenerate`-built, matches Python's `DEFAULT_ROAD_LENGTH_M`), RSUs
  at X=500/1500 (matches Python's `DEFAULT_RSU_POSITIONS`) -- **verified
  2026-08-16** (`convBoundary="0.00,0.00,2600.00,0.00"`, RSU `Vector`s
  confirmed in `v2x_environment.h`, trace X-coordinates genuinely span
  15.69-2316.62, not clipped). An earlier version of this was accidentally a
  1000m road (see "Resolved bugs" below) -- if road length or RSU positions
  ever look different from this again, treat it as a regression, not a
  variant.
- `src/maro_pe/env/ns3_sumo_env.py` -- Gym wrapper. Reshapes ns3gym's flattened
  Box observations back to `(n_vehicles, 12)`, parses `BuildExtraInfo()`'s JSON
  into `infos`, populates `rewards[i]` from `u_otr`.
- `scripts/ns3_eval_ma_rope.py` -- loads a real trained MA-ROPE checkpoint
  (from `CAMPAIGN_LATENCY_FIX_20260815`) and evaluates it (greedy actions,
  `evaluate=True`) against the ns-3 backend, computing Fleet OTR/PRR/u_otr_active
  from real per-step outcomes. This is what produced the headline result above.

## u_otr_active: correctly computed now, but low-signal -- don't use it to compare configs yet

Two bugs were found and fixed in sequence here (2026-08-16), both worth knowing
about if this number ever looks wrong again:

1. **OTR-vs-PRR mislabeling** (fixed): the utility formula's reliability term
   used `GetEmpiricalPrr()` (raw reception ratio) while being labeled/reported
   as "u_otr". Fixed to use a new `GetEmpiricalOtr()` (deadline-aware, mirrors
   `rx_on_time_counters`).
2. **Local-computing hardcode inverted** (fixed): `otr_val` was hardcoded to
   `1.0` for `rat_idx==0` (local-only) actions, reasoning "local is always on
   time." The real Python source (`environment.py` line ~431) deliberately
   hardcodes this to `0.0` -- a penalty for not offloading, not a reward.
   This alone explains why `u_otr_active` was pinned at ~0.90 regardless of
   N/seed/episode before the fix, and drops to ~0.35 after -- confirmed via
   C++ debug logging showing `otr_val=1` on every single sampled step
   pre-fix.

**After both fixes, `u_otr_active` sits consistently around 0.345-0.355**
across all N/seeds -- much narrower than Fleet OTR's 0.77-0.89 range over the
same runs. This is *not* a bug (verified by reading raw per-episode CSV values
directly, not just aggregate means) -- it's a real consequence of `e_ratio`
being hardcoded to `0.0` in the C++ utility formula (`std::exp(-0.0) = 1.0`,
a large *constant* additive term in every single calculation, roughly 0.15-0.40
depending on task type). That fixed floor dilutes the visible signal from the
genuinely variable terms (`otr_val`, `l_ratio`, `delta_cbr`).

**Open, unverified hypothesis, explicitly not blocking:** the Python source
computes a *real* (if already-known-invalid, see Energy section below)
`e_ratio_val` from the actual energy formula instead of hardcoding it to 0,
and that formula can go negative, making `exp(-e_ratio_val) > 1`, which
inflates Python's u_otr before it gets clamped to 1.0 -- plausibly explaining
the remaining ~0.35 (ns-3) vs ~0.52 (Python) gap. Not yet confirmed
numerically (would need re-running one Python seed with `e_ratio_val` forced
to 0 and comparing). Low priority -- do this only if `u_otr_active` needs to
become a trustworthy comparison metric for some future purpose; Fleet
OTR/PRR are the metrics that already answered the question that mattered.

## Energy: still out of scope, same reason as always

Neither side computes a real energy term. C++ hardcodes `e_ratio=0.0`
(documented in `channel_model.h`'s header). Python's `environment.py` energy
formula is the same one established invalid in `ENERGY_METRIC_DECISION.md`
(can go negative by construction). Porting it would just reproduce a known
bug in a second language -- not done, not planned, unless someone explicitly
scopes designing a valid energy model as its own piece of work.

## Resolved bugs, chronological (for context if something regresses)

1. **State dimension** (2026-08-15) -- `train_b3_baselines.py` hardcoded
   `state_dim=20`, unrelated to ns-3, predates this work. Fixed by removing
   the override (agent's correct default is 12). Did not affect
   `CAMPAIGN_CORRECTED_20260803` (used a different script with the correct
   value throughout).
2. **Aug 3 channel-validation run was broken, not conclusive** -- investigated
   2026-08-15, root-caused by AG via `mac_sanity_check.cc` (minimal 2-node
   test) to a broken custom socket/application layer in the legacy
   `channel-validation.cc`, not the PHY/MAC physics themselves. The original
   question (does the analytical model match real ns-3 physics) was reopened
   and is what the rest of this document answers.
3. **log10 latency bug** (2026-08-15) -- `env/environment.py`'s
   `baseline_recreation` branch computed local-compute latency as
   `log10(l_local) * (1-rho)` instead of the documented linear
   `l_local * (1-rho)`, compressing the local term to near-zero and breaking
   the parallel-execution `max()` model. Same "literal formula from the
   guide" pattern as the already-known-invalid energy formula. Fixed via an
   isolated one-line patch (both in `_claude_workspace/env/environment.py`,
   which produced `CAMPAIGN_LATENCY_FIX_20260815`, and independently in
   `src/maro_pe/env/environment.py` and `v2x_environment.h`). Verified: MA-ROPE
   still beats AllOffload decisively after the fix (DRR 0.955 vs. v25's
   0.951) -- the paper's core conclusion survives, though absolute Fleet OTR
   points dropped ~5-8pp. **Not yet folded back into the paper (v25 still
   reflects pre-fix numbers) -- that's a separate, not-yet-made decision.**
4. **Road length / RSU position mismatch** (2026-08-16) -- the SUMO network
   was briefly a 1000m road (vs. Python's 2600m) with RSUs at X=250/750 (vs.
   500/1500), which would have confounded any comparison with a spatial-density
   difference unrelated to physics fidelity. Fixed via `netgenerate` at
   2600m + reverted RSU positions; verified above.
5. **otr_val bugs (2x)** -- see "u_otr_active" section above.

## Finding, still needs a decision (paper-level, not ns-3-specific): Jakes fading negligible in baseline_recreation mode

`compute_jakes_fading()` returns ~1e-7 dB (effectively zero) for LTE/5G-NR
even at 20-30 m/s under `mode="baseline_recreation"` -- the mode behind every
validated Python number, v25 and the latency-fix retrain alike. Root cause:
that branch uses `freq_ghz` directly in the Doppler formula without
converting to Hz. **This means Fig. 12 in the paper and the "Jakes ✓" claim
in Table I may not reflect what the validated campaigns actually modeled.**
Not yet root-caused all the way to "does it change any reported number," not
yet reflected in the paper. This is orthogonal to the ns-3 work -- it's a
property of the Python model both sides are being validated against -- but
worth resolving before any future paper revision.

## Next steps, in rough priority order

1. **Decide whether/how to fold the log10-latency fix into the paper.**
   v25 currently reports pre-fix numbers; the fix is validated (retrained,
   DRR survives) but not yet reflected anywhere in the manuscript. Not an
   ns-3 task, but blocks calling this line of work "closed."
2. Extend the ns-3 sweep from 3 seeds to 5, matching both Python campaigns'
   sample size, for a fully like-for-like comparison.
3. (Low priority, not blocking) Verify the energy-term hypothesis for the
   remaining u_otr_active gap, or better: make both sides handle the energy
   term identically (most likely: zero it on the Python side too, matching
   the paper's already-established "energy is invalid, don't report it"
   position) rather than reconciling two different broken/simplified
   treatments.
4. Fix `ns3_eval_ma_rope.py`'s output path (writes to repo-root `results/`
   despite the string suggesting `_claude_workspace/results/`).
5. If/when this environment is ever used for *training* (not just evaluating
   frozen checkpoints), re-audit the reward pathway once more end-to-end --
   everything verified so far was evaluate-only (`evaluate=True`), so no
   reward-signal bug has actually been exercised by gradient updates yet.
