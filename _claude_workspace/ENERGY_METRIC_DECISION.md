# ENERGY_METRIC_DECISION.md

Workstream 1 (per the endorsed plan: "prove or remove, nothing in between"). Traced the defect to
its exact source in `env/environment.py`. Verdict below is decisive, not a hedge.

## What the code actually does

`env/environment.py` computes energy two entirely different ways depending on `self.mode`, and this
matters enormously: **the canonical pipeline (`env_mode="baseline_recreation"`) — the only mode this
entire reproduction, both Path A and Path B, has ever used — takes the first branch, never the
second:**

**Branch 1 — `mode in ["baseline_recreation", "legacy_guide"]`** (lines 278-309, comment reads
`"# Literal energy formula"` / `"# Literal rendering formula"` in the code itself):

```python
# local-only case (no offload):
e_total = P_CPU_W * math.log10(max(c_ratio, 1e-9))   # c_ratio = cpu_cycles / CPU_FREQ_HZ

# offload case:
term1 = P_CPU_W * log10(c_ratio)
term2 = tx_energy_mj * log10(D_ms / (1 - rho))
term3 = 1.0 * rho * log10(rho)
e_total = term1 + term2 + term3
```

**Branch 2 — every other mode** (lines 310-316), the one with the previously-known `energy_mode`
unit-conversion switch:

```python
e_tx = tx_energy_mj * data_mb * rho
if energy_mode == "energy_si_corrected":
    e_tx = e_tx / 1000.0        # <- the mJ->J fix already exists in the codebase
e_total = P_CPU_W * (l_local * (1 - rho) / 1000.0) + e_tx
```

## Why "prove" is not achievable, confirmed directly (not inferred)

The `energy_si_corrected` unit-conversion fix that `ENERGY_UNIT_IMPACT_REPORT.md` (prior audit)
proposed **only exists in Branch 2 and is never reached by `baseline_recreation` mode** — it is
dead code for every result this reproduction has ever produced. The actual problem in Branch 1 is
not a units mismatch; it's that the formula is not an energy equation at all. Confirmed with the
simplest possible case: for any local-only task (no offload — this is every NoOffload step and most
MA-ROPE steps), energy is `P_CPU_W * log10(c_ratio)`, where `c_ratio = cpu_cycles/CPU_FREQ_HZ`
ranges roughly 0.05-1.0 for this simulator's task types. `log10` of a fraction below 1 is always
negative — so this formula produces **negative energy for the most common case in the simulator, by
construction, regardless of any unit convention.** This single fact, checked directly against the
code (not the prior audit's report, though it agrees), is sufficient on its own: there is no unit
correction that makes `P_CPU_W * log10(fraction)` into a physically valid non-negative energy
value. The formula would need to be replaced, not rescaled.

## Why "remove" is the only defensible option within current scope

Replacing Branch 1's formula with something dimensionally sound is a real fix, but it is **not a
minor correction** — it changes the actual computation that produced every other number in this
reproduction's history, and per the prior audit, even the existing (dimensionally sound) Branch 2
formula, under its own SI-corrected setting, still does not match the manuscript's claimed value
(0.4591 J corrected vs. 0.7057 J claimed) — so fixing the formula would not, by itself, resolve the
larger Issue-class-2 question (`MANUSCRIPT_IMPACT_MEMO.md`) about whether Dataset A reflects a
different model version entirely. Switching to Branch 2's mode outright is not a narrow energy fix
either — `mode` is a simulator-wide switch that also changes the latency formula and queue-workload
gating (`CLAUDE_FINDINGS.md`'s root-cause #1 discussion), which would mean re-running the entire
campaign under a different physical model — a redesign decision, explicitly out of scope
("do not redesign the simulator").

## Verdict: REMOVE

**Energy cannot currently be reported for the `baseline_recreation` canonical pipeline — not because
the numbers are merely off, but because the formula computing them is not a valid energy equation
under any unit convention.** Recommend removing Energy from the corrected result tables and the
manuscript's headline comparison entirely, with a disclosed footnote explaining why, rather than
either reporting a number known to be invalid or attempting an in-scope "fix" that doesn't exist.

**If Energy reporting is wanted in the paper**, the only path is a scoped, explicit decision to
design and validate a real energy formula for `baseline_recreation` mode (not swap to Branch 2's
mode, and not just adjust Branch 1's units) — this is new scientific/engineering work requiring its
own sign-off, not something to do silently as part of this workstream. Not undertaken here.
