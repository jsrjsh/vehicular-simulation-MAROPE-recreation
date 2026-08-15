# NS3_SUMO_STATUS.md

Status of the SUMO + ns-3 co-simulation integration, on `experiment/city-scale`.
Read this before starting a session on this work, in either Claude or Antigravity --
this file is the single source of truth so the two don't drift out of sync.

## Objective

Replace the deterministic Python `V2XEnv` with a SUMO (mobility) + ns-3 (network
physics) co-simulation, **without regressing performance relative to v25's
validated results**. v25's numbers (`CAMPAIGN_CORRECTED_20260803`, hash-verified,
audited 2026-08-14) are the benchmark: MA-ROPE 88.8% fleet OTR / 0.951 DRR at
N=32 vs AllOffload's 12.5% / 0.367. Any ns-3-derived result that materially
undercuts this needs to be understood, not silently accepted, before being
reported anywhere.

## What's actually working (plumbing only, not physics)

- `src/maro_pe/env/ns3_sumo_env.py` -- `Ns3SumoV2XEnv`, a Gym-compatible wrapper
  bridging to an external ns-3 process over ZeroMQ (port 5555) via `ns3gym`.
- `src/maro_pe/simulation/ns3_script.cc` -- minimal ns-3 C++ script implementing
  `OpenGymInterface`, spawns a 32-node container, basic mobility model,
  12-dimensional state vector (matches the original MA-ROPE state space --
  see dimension note below).
- `src/maro_pe/simulation/sumo_scenario/{sumo.net.xml, sumo.rou.xml, sumo.sumocfg}`
  -- foundational SUMO road network + route assets. Not yet wired into ns-3's
  mobility model.
- `scripts/train_federated.py` and `scripts/train_b3_baselines.py` accept
  `--environment-mode ns3_sumo` and will instantiate `Ns3SumoV2XEnv`.
- Verified 2026-08-15: 5-episode smoke tests of both scripts connect over the
  ZeroMQ/OpenGym bridge and complete without crashing.
- `src/maro_pe/simulation/channel_model.h` -- line-for-line C++ translation of
  `env/channel.py` (path loss, Jakes fading, SINR, link-success sigmoid) plus
  the channel-relevant fields of `env/config.py::RAT_SPECS`. Verified
  2026-08-15 against golden values computed from the real Python functions
  (`scripts/compute_channel_model_golden_values.py` +
  `channel_model_golden_test.cc`, 5 test cases across all 4 non-Local RATs,
  both modes, all passing to 1e-9). **Not yet called from `ns3_script.cc`'s
  OpenGym callbacks** -- it's a standalone, independently-tested module ready
  to be wired in, not integrated yet. Energy is deliberately excluded from
  this port -- see the file's header comment for why.

**That's it, plus the untested `channel_model.h` module above.** SUMO traces
aren't driving node mobility yet, and nothing in `ns3_script.cc` calls the
new physics functions yet. Nothing produced by the OpenGym pipeline so far
constitutes a network-fidelity result -- it only proves the wiring works. Do
not cite these runs as validating anything physical.

## Finding, needs a decision: Jakes fading is numerically negligible in baseline_recreation mode

While generating the golden values above, `compute_jakes_fading()` returned
~1e-7 dB even for LTE/5G-NR at 20-30 m/s under `mode="baseline_recreation"`
-- the mode that produced every one of v25's validated numbers. Root cause:
the baseline_recreation branch uses the RAT's `freq_ghz` value (e.g. 1.8 for
LTE) directly in the Doppler-shift formula without converting it to Hz
(`f_D = speed * freq_ghz / c`), unlike the `physically_corrected` branch
which does convert (`freq_ghz * 1e9`). That makes `f_D` about 9 orders of
magnitude too small, which makes the coherence time `T_c` enormous, which
makes the fading term collapse to ~0 regardless of speed. Confirmed
side-by-side: identical inputs (300m, 20 m/s) give 0.0000000646 dB under
baseline_recreation vs. 2.05 dB under physically_corrected -- the corrected
formula is the one producing a physically sensible fading magnitude.

**This means Fig. 12 in the paper ("Jakes Fading: Cellular RAT SINR
Degrades with Speed") and the "Jakes" checkmark MA-ROPE claims in Table I's
feature-coverage matrix may not reflect what the validated campaign
actually modeled** -- if baseline_recreation's Jakes term is always
negligible, cellular RAT SINR in the validated results doesn't meaningfully
degrade with speed via fading at all; whatever speed-dependence exists in
the reported figures would have to come from elsewhere. This is a new
finding, not yet root-caused all the way to "does it change any reported
number," and not yet reflected anywhere in the paper. Flagging here rather
than silently working around it in the ns-3 port, since the physics port
needs an explicit decision: replicate baseline_recreation's Jakes formula
faithfully (matching v25 exactly, negligible fading and all), or use the
physically_corrected formula (physically sensible, but then results won't
match v25 and that mismatch needs to be understood before comparing).
Recommend faithful replication for the first N=8/16/32 comparison against
v25 (next steps below), with the units question raised as its own separate
decision afterward -- don't conflate "port the model" with "fix the model"
in the same pass.

## State dimension -- resolved 2026-08-15

The ns-3 environment briefly emitted a 20-dim mock observation to paper over a
crash; root cause was a separate, pre-existing bug: `train_b3_baselines.py`
hardcoded `D3QNAgent(state_dim=20, ...)` for both `shared` and
`independent/fedavg` modes, overriding the agent's correct default of 12.
Fixed by removing the explicit override (confirmed `D3QNAgent.__init__`
defaults `state_dim=12`). `ns3_sumo_env.py` now correctly emits 12 dims,
matching the original state space and the existing trained-checkpoint
architecture.

**Open question, not yet resolved:** that `state_dim=20` bug predates this
integration entirely and has nothing to do with ns-3. It's unknown whether
`train_b3_baselines.py` was ever run directly (as opposed to via
`_claude_workspace/scripts/run_corrected_campaign.py`, which always hardcoded
the correct `state_dim=12` and is what actually produced v25's validated
numbers -- those are unaffected). If `train_b3_baselines.py` was used to
produce any reported result anywhere, that result trained on a mismatched
dimension and should be checked before being trusted.

## Explicitly not folded in

- `vehicular-simulation/ns-3/` -- the ns-3 engine itself (ns-allinone-3.37 +
  ns3gym). Third-party build dependency, gitignored, never committed. Fetch
  and build locally per ns-3's own instructions; register `ns3gym` from
  `contrib/` as AG's original setup did.
- `configs/experiments/paper_main.yaml` was deliberately left untouched.
  `env_type` is not consumed by any script (checked 2026-08-15) so adding it
  there would currently be a no-op -- but that file drives the validated
  paper-reproduction pipeline, so it must never silently redirect to this
  experimental environment even after `env_type` is eventually wired up.
  Use `configs/experiments/ns3_sumo_dev.yaml` instead for this work.
- The `archive/`, `results/`, `checkpoints/`, `manuscript/` etc. duplicated
  inside the old `ns3-sumo-version/` working copy were stale snapshots of
  content already tracked elsewhere -- not carried forward.

## Resolved: the Aug 3 channel-validation run was broken, not conclusive

`_claude_workspace/EXECUTION_CONTRACT_V4_SUMO_NS3_VALIDATION.md` scoped an
offline validation (2026-08-03) comparing the analytical channel model
(`env/channel.py`) against a real ns-3 simulation
(`vehicular-simulation/scratch/channel-validation.cc`), producing
`results/SUMO_NS3_VALIDATION_20260803/SUMO_NS3_CHANNEL_VALIDATION_REPORT.md`.
That report showed ~99% divergence for LTE and ~91% for WiFi-6 (analytical
predicts near-100% success, ns-3 empirical shows near-0%) and was never
followed up with a decision document or reflected anywhere in the paper.

**Investigated 2026-08-15.** From the raw CSV
(`vehicular-simulation/simulation_results_channel_validation.csv`, 9,716
rows): 99.86% of attempts logged `TIMEOUT`, only 14 `SUCCESS`, and the
recorded "Latency" for timeout rows was literally the hardcoded per-task
deadline (0.05 / 0.4 / 2.0 s) being logged when the timeout fired -- not a
measured network latency. Success rate was 0% even at the 2-second deadline
(40x the shortest), ruling out "deadline too tight for connection setup."

**Root cause confirmed 2026-08-15 (AG).** A minimal diagnostic
(`mac_sanity_check.cc`: 2 static nodes, 1m apart, 20 dBm, `AdhocWifiMac`,
standard `UdpEchoClient`/`UdpEchoServer` apps instead of the legacy script's
custom application) delivered a packet end-to-end cleanly -- 2.93ms one-way,
exactly as expected for 802.11a OFDM at close range. This confirms ns-3's
PHY/MAC stack itself is fine. The legacy `channel-validation.cc`'s custom
application/socket layer had a configuration bug (likely missing explicit
`SetStandard`/`SetRemoteStationManager` calls), not the physical channel
model. **The original validation question -- does the analytical model hold
up against real ns-3 physics -- is still open** (this only proved the
harness was broken, not that the model is right or wrong), but the
MAC/routing baseline is now verified sane, so the physics port below can
proceed without inheriting this failure mode.

## Next steps, in order

1. ~~Port the physical-layer formulas from `env/channel.py` into C++~~ --
   **done 2026-08-15**, see `channel_model.h` above. Remaining sub-steps:
   - **Wire `channel_model.h` into `ns3_script.cc`'s OpenGym callbacks**
     (`MyGetObservation`, `MyExecuteActions`, `MyGetReward` currently return
     mocked/constant values -- replace with real calls into
     `ComputeSinrDb`/`ComputeLinkSuccess`, drawing random samples from ns-3's
     own RNG at the call site, matching `channel_model.h`'s dependency-injection
     design).
   - Port `env/environment.py`'s task generation, RSU queue model, deadline
     classification (on-time/late/failed), and 12-dim observation assembly
     (including the 0.5 "unknown RAT" default from two conversations ago) --
     not yet started, this is the bulk of remaining `env/` logic beyond the
     channel model itself.
   - Energy is explicitly NOT in scope (see `channel_model.h` header) --
     v25 doesn't report it either, for the same reason (the implemented
     formula is invalid; see `ENERGY_METRIC_DECISION.md`).
2. **Wire SUMO mobility into ns-3** via `Ns2MobilityHelper`, consuming a
   `sumo_trace.xml` export instead of the current basic mobility model.
3. Once both land: run the same N=8/16/32 density sweep used for
   `CAMPAIGN_CORRECTED_20260803` and compare Fleet OTR / DRR against v25's
   numbers directly. Large deviations need root-causing before being reported,
   not averaging away. Use `mode=baseline_recreation` for this comparison
   (see the Jakes-fading finding above on why mode choice matters here).
4. Only after step 3 passes a real audit does this environment become a
   legitimate replacement to reference in the paper or announced future work.
