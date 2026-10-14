You are continuing the SUMO (city-scale mobility) work for the MA-ROPE V2X task-offloading project. Another chat owns the journal paper, so you must work in isolation.

## Where things are
- Repo (Track A): /Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation  (branch experiment/city-scale)
- READ FIRST: NS3_SUMO_STATUS.md in that repo. It is the single source of truth: a SUMO + ns-3 co-simulation already exists (src/maro_pe/simulation/*.h, ns3_script.cc, sumo_scenario/, env/ns3_sumo_env.py, scripts/ns3_eval_ma_rope.py, ns3_eval_baselines.py). Core physics validation was finished on 2026-08-16: fleet OTR matched the Python baseline within about 3 points at N=8/16/32, but only on a 2600 m, 2-RSU corridor, which is NOT city-scale.
- Paper (do not touch): MA_ROPE_TVT_LATEX_v24_PureSim/ inside that repo. Track B (do not touch): /Users/aryaveersingh/Projects_Claude/01_Engineering/MA_ROPE_Grok.
- Old AG copy (reference only): /Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation_SUMO_ns3_antigravity (3.2 GB, do not copy it wholesale).

## Isolation rules
1. Create a git worktree on a NEW branch (for example city-scale-sumo, from experiment/city-scale) in a new folder next to the repo, and work only there. Never edit files in the paper folder or in MA_ROPE_Grok. No git push.
2. Record every result with the commit hash, simulator mode, seed, N and protocol. Keep one VERSION_LOG.md in the worktree listing each version, what changed, and its results, so a later reader can tell which numbers belong to which version.
3. Ask me before any run longer than about 30 minutes or any download of maps or large data.

## Goal
Build a true city-scale SUMO scenario (an urban grid or a real road extract of a few km, multiple RSUs with coverage ranges, vehicle counts N = 8, 16, 32, 64 and more) and run the existing ns-3 co-simulation on it, then compare against the Python simulator's corrected baselines.

## Facts you must know (verified on 2026-10-13/14)
- The paper's numbers come from simulator mode baseline_recreation plus three bug fixes (Jakes units, linear local-latency term, reset() sets is_new_task). The Python copy in MA_ROPE_Grok/codebase/env reproduces the paper's baseline per-seed numbers exactly. Use that as the physics reference.
- Latency is dominated by a linear queue model: backlog Q_r = sum of requested offload ratios at RSU r, delay = Q_r x 50 ms. Link throughput does not enter latency. Any city-scale version needs a defined behaviour for several RSUs and handovers.
- The paper-reward MA-ROPE policy makes zero offload attempts when exploration is off; the reported OTR comes from epsilon = 0.05 evaluation exploration. Do not use fleet OTR alone. Report an all-task on-time rate (local and offloaded tasks) and greedy (epsilon = 0) behaviour as well.
- OTR counts offloaded packets only, so NoOffload scores 1.0 by construction.
- Training is not reproducible from the seed (torch weights are never seeded). Seed torch in anything you run. ns3gym's reset() also reuses the same simSeed per object; the status file describes the fix.
- Single-RAT, fixed-rho and queue-hidden ablations were not worse than full MA-ROPE; only FedAvg mattered.

## Deliverables
1. A plan first (scenario design, RSU placement, N values, what is compared, estimated compute). Wait for my approval.
2. The SUMO scenario files and any needed changes to V2XEnvironment (multi-RSU coverage, handover).
3. A validation table: Python reference vs ns-3 on the new scenario, with mean and std over seeds, held-out episodes, safety-only metrics and the all-task on-time rate.
4. Update NS3_SUMO_STATUS.md in the worktree and write VERSION_LOG.md. Tell me which results, if any, would change a claim in the paper.
