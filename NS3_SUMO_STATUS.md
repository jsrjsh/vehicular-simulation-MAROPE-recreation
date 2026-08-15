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

**That's it.** No SINR/path-loss/energy formulas have been ported into the C++
side, and SUMO traces aren't driving node mobility yet. Nothing produced by
this pipeline so far constitutes a network-fidelity result -- it only proves
the wiring works. Do not cite these runs as validating anything physical.

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

1. **Port the physical-layer formulas** from `env/channel.py` /
   `env/environment.py` (SINR, path loss per RAT, the energy model) into
   `ns3_script.cc`. Build in boundary assertions while doing this (energy
   \>= 0, probabilities in [0,1]) -- this is exactly the class of bug the
   Python simulator had (see `_claude_workspace/ENERGY_METRIC_DECISION.md`)
   and it should not be repeated on the ns-3 side. While doing this, sanity
   check against the open item above -- confirm a trivial link succeeds
   before trusting any distance/RAT-dependent numbers.
2. **Wire SUMO mobility into ns-3** via `Ns2MobilityHelper`, consuming a
   `sumo_trace.xml` export instead of the current basic mobility model.
3. Once both land: run the same N=8/16/32 density sweep used for
   `CAMPAIGN_CORRECTED_20260803` and compare Fleet OTR / DRR against v25's
   numbers directly. Large deviations need root-causing before being reported,
   not averaging away.
4. Only after step 3 passes a real audit does this environment become a
   legitimate replacement to reference in the paper or announced future work.
