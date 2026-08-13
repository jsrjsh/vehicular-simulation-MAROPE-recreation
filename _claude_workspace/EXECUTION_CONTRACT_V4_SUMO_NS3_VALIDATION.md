# EXECUTION_CONTRACT_V4 — SUMO+ns-3 Channel Model Validation (Phase 1)

Scope: offline validation only. Does NOT couple ns-3 to the RL training loop, does NOT port
D3QN/FedAvg/LDP into C++, does NOT touch `env/` Python code. Goal: produce a quantitative,
honest answer to "how well does the analytical Shannon/SINR channel model
(`env/channel.py`) match a real ns-3 MAC-layer simulation under realistic SUMO mobility" —
directly closing the gap flagged in the revision's Limitations 7.1.

## What already exists (do not rebuild)
`vehicular-simulation/` in this repo already has: a SUMO 3x3 grid network
(`map.net.xml`, `map.rou.xml`), a generated NS-2 mobility trace (`mobility.tcl`, from
`generate_mobility.py`), a compiled ns-3.41 tree (`ns-3/`, modules: core, network, mobility,
internet, wifi, lte, propagation), and a C++ driver (`scratch/vehicular-offloading.cc`)
implementing 4 heuristic offload strategies with CSV output
(`Time,VehicleID,TaskID,TaskType,Decision,Latency,Success,WifiConnected,Status`).
Its own `MA_ROPE_RECONSTRUCTION_PLAN.md` correctly identifies this as heuristic-only — no RL,
no FedAvg, no privacy — and flags the Python/C++ coupling problem. This phase does not solve
that coupling problem; it sidesteps it by keeping the comparison offline.

## Task
1. Extend `scratch/vehicular-offloading.cc` (or add a new scratch program alongside it,
   don't modify the existing one destructively) to additionally log, per transmission
   attempt: RAT/technology used, distance from vehicle to RSU/BS at the moment of
   transmission, vehicle speed, and success/failure outcome. Log instantaneous SINR too if
   it is readily accessible from ns-3's PHY trace hooks for the module in use; if not
   trivially accessible, success/failure vs. distance is an acceptable fallback — state
   which was used.
2. **Known module gap, handle honestly, do not fake it**: the currently-built ns-3 only
   includes `wifi` and `lte` modules. Our Python model has 4 RATs (LTE, ITS-G5, 5G-NR,
   WiFi-6). ns-3's `lte` module gives a real LTE analog. ns-3's `wifi` module with 802.11ax
   settings gives a real WiFi-6 analog. ns-3 does **not** natively support 5G-NR (would
   require the separate 5G-LENA module, not installed) or ITS-G5/802.11p (would require the
   `wave` module, not installed). Do not substitute LTE parameters and call it 5G-NR, and do
   not skip logging this gap. Two acceptable paths, pick one and disclose which:
   (a) install the `wave` module (802.11p) for an ITS-G5 analog — feasible, same wifi family
   — and scope this phase to 3 of 4 RATs (LTE, ITS-G5 via 802.11p, WiFi-6), explicitly
   deferring 5G-NR validation as a named follow-on needing 5G-LENA; or
   (b) scope this phase to the 2 natively-available RATs (LTE, WiFi-6) only, and name both
   ITS-G5 and 5G-NR as deferred. Either is fine — state which and why in the report.
3. Run the driver across the same distance range implied by `env/config.py`'s
   `DEFAULT_ROAD_LENGTH_M` (2600m) and `DEFAULT_RSU_POSITIONS` ([500, 1500]), and across a
   representative vehicle-speed range (use the SUMO trace's actual speed distribution, don't
   invent one). Vehicle count can follow the existing SUMO grid's natural traffic level —
   note actual count achieved, don't force-fit to exactly 8/16/32 if the grid doesn't
   naturally produce that.
4. From the resulting CSV, compute the empirical link-success rate as a function of distance
   (binned) for each validated RAT.
5. Independently, using `env/channel.py`'s `compute_sinr()` and `compute_link_success()`
   functions directly (import and call them, don't reimplement), compute the analytical
   model's predicted link-success rate at the same distances, same RAT specs
   (`env/config.py::RAT_SPECS`), same mode (`physically_corrected`).
6. Report, per validated RAT: the empirical curve, the analytical curve, and the divergence
   (mean absolute difference in success probability across the tested distance bins). No
   interpretation beyond stating the numbers — is the model closer/further at short vs. long
   range, does it over- or under-predict reliability.

## Provenance requirements (same as every prior deliverable in this project)
Exact commit hash of `vehicular-simulation/` at run time, ns-3 version/module list actually
compiled, SUMO network/route file hashes, exact command used to run the scratch program, raw
CSV output paths, and the exact script used to compute the analytical-model comparison
(save it, don't compute inline and discard). Do not touch `env/`, `agents/`, or any file
under `results/CAMPAIGN_*` — this phase produces its own new output directory
(`results/SUMO_NS3_VALIDATION_<date>/`), fully separate from every existing campaign.

## Explicitly out of scope for this phase (do not attempt)
Do not build an ns3-gym bridge. Do not export the D3QN model into C++. Do not re-run MA-ROPE
training or evaluation inside ns-3. Do not modify `vehicular-offloading.cc`'s existing 4
strategies' decision logic. If validation reveals the analytical model diverges
significantly, that is a valid and useful finding to report — it does not obligate building
the full online coupling in this same phase. That would be a separate, larger Phase 2,
scoped only if this validation motivates it.

## Deliverable
`SUMO_NS3_CHANNEL_VALIDATION_REPORT.md` — per-RAT empirical vs. analytical comparison,
methodology, provenance block, and an explicit statement of which RATs were validated vs.
deferred and why (module coverage, not convenience).
