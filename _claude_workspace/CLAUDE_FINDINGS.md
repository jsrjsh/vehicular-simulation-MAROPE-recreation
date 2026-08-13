# MA-ROPE Findings Log (Claude — isolated workspace)

Working area: `_claude_workspace/` inside the connected `Projects_Claude` copy. Nothing here
touches the Antigravity repository. This file is the provenance ledger substitute for git commits
(git writes are blocked in this sandbox — `.git/index.lock` cannot be removed, "Operation not
permitted" — so milestones are logged here instead, dated and with exact commands/evidence).

## 2026-08-02 — Environment stood up

- `torch==2.13.0` (PyPI default on this aarch64 sandbox) hard-requires NVIDIA CUDA shared libs at
  import time even for CPU use (`libcudart.so.13` missing) and pulls ~1.5-2GB of `nvidia-*` wheels
  that don't fit the sandbox's disk budget.
- Fix: pinned `torch==2.2.0` (last version with a clean CPU-only aarch64 dependency tree — no
  `nvidia-*` packages, per `pip install --dry-run torch==2.2.0`).
- torch 2.2.0 is built against numpy<2; the sandbox's pre-installed numpy 2.2.6 caused
  `RuntimeError: Could not infer dtype of numpy.float32` on any numpy→tensor conversion. Fixed by
  `pip install --break-system-packages "numpy<2"` → resolved to numpy 1.26.4.
- Verified with a smoke test replicating the actual `DuelingQNetwork` forward/backward/`optimizer.step()`
  pattern — works cleanly.

## 2026-08-02 — Baseline test suite run (before any fixes)

Command: `python3 -m pytest tests/ -q` on recovered source (`git show HEAD:<path>` for every file
under `env/`, `agents/`, `tests/`, `scripts/`, since these are absent from the working tree but
present in `HEAD`'s git tree).

Result: **73 passed, 3 failed.**

1. `tests/test_env.py::test_queue_delay_saturation` — `AssertionError: 0 != 0.25`
2. `tests/test_d3qn.py::test_loss_and_gradient_bounds` — `TypeError: must be real number, not tuple`
3. `tests/test_per.py::test_priority_epsilon_guard` — `AssertionError: 1e-06 != 1e-06`

## Root cause #1 (CONFIRMED): `V2XEnv.reset()` does not reinitialize `is_new_task`

`env/environment.py`, `step()` Section 1 gates whether a vehicle's offload workload is counted
toward `rsu_queues`:

```python
if rat_idx > 0 and rho > 0.0:
    if self.mode in ["baseline_recreation", "legacy_guide"] or self.is_new_task[i]:
        rsu_workloads[rsu_idx].append((i, rat_idx, rho))
```

`is_new_task[i]` is set only in two places: `__init__` (`{i: True for i in self.agents}`, once,
at object construction) and at the end of `step()` Section 7, where it's re-rolled stochastically
per vehicle (`task_arrival_prob`, ≈0.3) for the *next* step. **`reset()` never touches it.**

Reproduced directly (not just via pytest) — same `V2XEnv` object, three `reset()`+`step()` cycles
in sequence (mirroring the failing test exactly):

```
mode: physically_corrected
is_new_task right after 3rd reset(): {0: False, 1: False, 2: False, 3: True}
```

So by the third episode, three of four vehicles carry a stale `is_new_task=False` from the
previous episode's last stochastic roll into a freshly-reset episode where `reset()` *did* sample
them all fresh tasks — the flag and the actual task state disagree. Any vehicle with a stale
`False` has its offload workload silently dropped from `rsu_queues`/`rsu_cbr_curr` for that step,
in any `mode` other than `baseline_recreation`/`legacy_guide` (which bypass the flag entirely).

**Impact**: every training/eval run that calls `reset()` more than once on the same environment
instance (i.e. every multi-episode run — which is all of them) has nondeterministically corrupted
RSU-queue accounting after the first episode, with the corruption's magnitude depending on RNG
state carried across episodes. This is the most plausible mechanistic explanation yet found for
why the manuscript's queue-loss numbers have been inconsistent across versions (1.15%, 0.85%,
2.14%, 38.0%, 1.3% at various points) — different runs/seeds/episode counts would hit different
amounts of this corruption.

**Fix applied** (`env/environment.py`, inside `reset()`'s per-vehicle loop, right after
`self.active_tasks[i] = self._sample_task()`): added `self.is_new_task[i] = True`, since every
`reset()` call does sample a genuinely new task for every vehicle.

**Verification**: `test_queue_delay_saturation` passes after the fix; re-ran the full suite from a
clean `/tmp` copy (avoids an unrelated sandbox artifact, see below) — no regressions.

## Root cause #2 (CONFIRMED): inconsistent unpacking of `agent.learn()`'s return value

`agents/d3qn/agent.py`'s `learn()` returns a 2-tuple `(loss, mean_q)` on every code path (both the
early-return-if-buffer-too-small branch and the normal training branch), despite its own type
hint (`-> float`) and docstring implying a scalar.

Grep across `scripts/*.py` for `.learn()` call sites:

- `scripts/train_b3_baselines.py:182` — `loss, q_val = agent.learn()` — **correct**, and uses
  `q_val` downstream for average-Q logging.
- `scripts/train_single_agent.py:156` and `scripts/train_federated.py:212` — `loss = agent.learn()`
  followed by `if loss > 0.0:` — **incorrect**: assigns the tuple to `loss`, and
  `tuple > float` raises `TypeError` in Python 3. These two scripts could not have completed a
  real training run against this version of `agent.learn()` without crashing on the first learning
  step (as soon as the replay buffer reaches `batch_size`).
- All other call sites (`evaluate_marope_calibrated.py`, `exp001.py`, `exp002.py`,
  `reproduce_paper_sweeps.py`, `run_marope_calibration.py`, `run_marope_fasttrack_n8.py`,
  `run_stage2_pilot.py`, `run_validation_training.py`, `train_federated.py:69`,
  `train_single_agent.py:58`) call `.learn()` without capturing the return value — unaffected.

Since `train_b3_baselines.py` unpacks correctly and actively uses both values, the tuple return is
the intended/current API — not a bug to remove. `train_single_agent.py` and `train_federated.py`
are the stale call sites (most likely left over from before `learn()` was extended to also report
mean Q, based on `train_b3_baselines.py`'s naming and the `recreation-b3.2-frozen` tag in the
branch it corresponds to).

**Fix applied**: unpacked the tuple correctly in `train_single_agent.py:156` and
`train_federated.py:212` (`loss, _q_val = agent.learn()`), matching the working pattern in
`train_b3_baselines.py`. Also fixed `tests/test_d3qn.py::test_loss_and_gradient_bounds`, which had
the same incorrect scalar-unpack bug.

**Verification**: `test_loss_and_gradient_bounds` passes after the fix.

## Root cause #3 (CONFIRMED, test-only, not a code bug): float32 precision in PER epsilon guard

`tests/test_per.py::test_priority_epsilon_guard` asserted
`self.assertEqual(buffer.priorities[0], 1e-6)`. `buffer.priorities` is a `numpy.float32` array;
`1e-6` is not exactly representable in float32 (stores as `9.9999999747524...e-07`), so exact
equality against the float64 Python literal `1e-6` fails on a pure representation artifact. The
underlying PER epsilon-guard logic is correct.

**Fix applied**: changed the assertion to `assertAlmostEqual(..., places=6)`.

**Verification**: passes after the fix.

## Sandbox artifact (not a code bug): file deletion blocked inside the synced workspace folder

Any test/script that creates and then deletes a file using a path relative to cwd *inside*
`_claude_workspace` (which lives under the host-synced `Projects_Claude` mount) fails with
`PermissionError: [Errno 1] Operation not permitted` on `os.unlink`/`shutil.rmtree` — e.g.
`tests/test_d3qn.py`'s `setUp`/`tearDown` uses `self.tmp_dir = "tests/tmp_d3qn"`. This reproduces
even for a bare `open(...).write(); os.unlink(...)` in the same directory, while the exact same
operations in true `/tmp` (not synced) succeed immediately. This is the same class of restriction
already seen with `.git/index.lock`. **Workaround used for verification runs**: copy `env/`,
`agents/`, `tests/` to `/tmp/<scratch>` before running `pytest`. Final/durable artifacts still get
written back into `_claude_workspace` (that part works fine — only delete-after-create inside the
synced tree is blocked). Scripts intended to run training loops under this mission should use
`tempfile.mkdtemp()` for any scratch files rather than a fixed relative path.

## Current test suite status

Command: `python3 -m pytest tests/ -q`, run from a clean `/tmp` copy of `env/`, `agents/`,
`tests/` as they currently stand in `_claude_workspace/`.

Result: **76 passed, 0 failed.**

## 2026-08-02 — Phase 3 kickoff: two distinct environments exist, and one "reproduction" script is a non-functional stub

While trying to run an actual training job (not just unit tests), found the codebase contains
**two separate, non-interchangeable environment implementations**:

- `env/environment.py` (`V2XEnv`) — the one investigated above. `state_dim=12`, 4 RATs
  (LTE/ITS-G5/5G-NR/WiFi-6, matching the manuscript's Fig. 4 description), per-RSU multi-queue
  accounting via `is_new_task`-gated `rsu_workloads`. Used by `scripts/train_single_agent.py` and
  `scripts/train_federated.py`.
- `env/environment_plus.py` (`V2XEnvPlus`) — `state_dim=20`, only 2 RATs (LTE/5G, 5 ρ-levels each,
  11 actions total but a different action table), a single global M/M/1-style MEC queue (`Q_t`)
  with an autoregressive background-load term, and a different reward decomposition
  (`w_s/w_t/w_e/w_q/w_o` weights). Used by `scripts/train_b3_baselines.py` — the script whose name
  matches the `recreation-b3-baseline` branch / `recreation-b3.2-frozen` tag in git history.
  **Does not contain `is_new_task` at all** — a structurally different queue model, not just a
  bugfixed version of the same one.

This means the `is_new_task` reset bug (root cause #1) is confirmed real and fixed, but its blast
radius is scoped to the `V2XEnv` path (`train_single_agent.py` / `train_federated.py`). Whether
`V2XEnv` or `V2XEnvPlus` is what actually produced the manuscript's currently-reported numbers is
still open — needs to be settled from `results/*.json` provenance (which script/config produced
which archived result file) before Phase 2's registry can be trusted. Do not assume one over the
other without checking.

Separately: **`scripts/reproduce_paper.py` is a non-functional stub.** Its `--reviewer-mode` and
full-reproduction code paths only print progress messages — the loop body is a comment
(`# In a real run, we would subprocess.call(['python3', 'scripts/train_b3_baselines.py', ...])
# For this template script, we simulate execution to demonstrate the structure`) with no actual
call, and it unconditionally prints `"[*] Comparing against paper tolerances... OK."` regardless
of anything. Anyone (or any prior audit) that ran this script and treated its "OK" output as
evidence of successful reproduction was working from a false signal. Flagging this explicitly
since it's exactly the kind of self-certifying-but-empty artifact this mission was commissioned to
catch.

## 2026-08-02 — First real (non-fabricated) end-to-end training runs

Ran `scripts/train_single_agent.py` (V2XEnv path) for 5 episodes after the `is_new_task` and
`learn()`-unpacking fixes — completes without error, produces real reward/loss/epsilon numbers,
writes a real checkpoint:

```
Episode 01 | Reward: 78.3988 | Loss: 0.0534 | Epsilon: 0.9018
...
Episode 05 | Reward: 83.1489 | Loss: 0.0976 | Epsilon: 0.4953
```

(Before the `learn()` fix, this script would have raised `TypeError` on the first learning step.)

Ran `scripts/train_b3_baselines.py` (V2XEnvPlus path, `--mode independent --n_vehicles 2
--episodes 2 --eval_interval 1 --eval_eps 1 --seed 42`) — also completes cleanly, real eval output:

```
[Ep 1] Eval Success: 1.000 | Latency (succ): 0.0075s | Energy: 0.0105J | ... Eps: 1.000
[Ep 2] Eval Success: 1.000 | Latency (succ): 0.0159s | Energy: 0.0087J | ... Eps: 0.953
```

These are toy-scale smoke runs (2-5 episodes, 2-4 vehicles) meant only to prove the pipelines
execute correctly end-to-end post-fix — not statistically meaningful and not to be compared
against manuscript numbers. Real Phase 3 runs (N=8/16/32, ≥5 seeds, full episode counts) are the
next step. Constraint to solve for that: this sandbox's shell tool caps each call at ~45 seconds
and does not preserve background/`nohup` processes between calls, so a multi-hour run has to be
chunked — e.g. lower episode counts per invocation with checkpoint resume, or restructuring the
training scripts to checkpoint-and-exit within the time budget across repeated calls. Not yet
solved.

## 2026-08-02 — RESOLVED: which environment/pipeline is canonical for the manuscript

Prompted by external review pushing back that I was fixing code without first establishing which
implementation is actually canonical. Settled it with direct evidence rather than inference:

**`scripts/reproduce_paper_sweeps.py` + `env/environment.py` (`V2XEnv`, `env_mode="baseline_recreation"`)
is the canonical manuscript pipeline.** Proof: its file-naming code —
`ckpt_path = f"{ckpt_dir}/ma-rope_seed_{seed}_ep_{episodes}_hash_{ckpt_hash}.pt"` and
`csv_filename = f"{out_dir}/{policy_type}_seed_{seed}_ep_{episodes}_hash_{ckpt_hash}.csv"` with
`mode_dir = "paper_reproduction" if env_mode == "baseline_recreation" else "physically_corrected"`
— matches the real files on disk in `results/paper_reproduction/n8/` and `.../n32/` exactly
(`ma-rope_seed_0_ep_5_hash_126ca59e.csv`, etc.), and its CSV header
(`env_mode,policy_type,seed,episode,u_prr_step,u_prr_active,u_otr_step,u_otr_active,fleet_otr,prr,
latency_active_ms,latency_step_ms,energy_active_j,energy_step_j,queue_loss,checkpoint_hash`) is an
exact vocabulary match to the manuscript's reported metrics (U_PRR, U_OTR, Fleet OTR, PRR, queue
loss). Policy names on disk (`ma-rope`, `nooffload`, `alloffload`) match the manuscript's named
baselines directly, at both N=8 and N=32.

**`scripts/train_b3_baselines.py` + `env/environment_plus.py` (`V2XEnvPlus`) is a separate,
parallel track — not the source of manuscript numbers.** Its archived outputs
(`results_{independent,shared,fedavg}_seed_{42-46}.csv` at the repo root, confirmed via matching
`csv_file = f"results_{args.mode}_seed_{args.seed}.csv"` and matching console-log format in the
paired `logs_*.txt` files) use a generic RL-benchmark schema (`reward, success_rate, latency_success,
latency_all, energy, queue, epsilon, td_loss, avg_q, ...`) — it has no `u_prr`/`u_otr`/`fleet_otr`
fields at all, and its environment only models 2 RATs (LTE/5G) against the manuscript's stated 4
(LTE/ITS-G5/5G-NR/WiFi-6). This is presumably the `recreation-b3-baseline` branch's own
self-contained ablation/robustness study, not something that ever fed the paper.

**Correction to root cause #1's scope**: the `is_new_task` bug I found and fixed is real and
correctly scoped to `V2XEnv`, but `env_mode="baseline_recreation"` — the mode the canonical
pipeline actually uses — bypasses the `is_new_task` gate entirely (`if self.mode in
["baseline_recreation", "legacy_guide"] or self.is_new_task[i]`, first branch always true). So
**this bug does not explain the canonical paper-reproduction pipeline's queue-loss numbers.** It's
still a real, worth-keeping fix (it matters for `physically_corrected`-mode runs, e.g.
`train_single_agent.py`'s default), but I was overstating its relevance before checking which mode
the actual manuscript pipeline uses. Flagging my own overreach here rather than letting it stand.

## 2026-08-02 — Actual root cause of queue-loss drift: mixed experimental campaigns in one directory

With the canonical pipeline identified, computed real `queue_loss` values directly from every CSV
in `results/paper_reproduction/n8/` and `.../n32/` (no fabrication — read straight from the archived
files). Two things stood out:

1. For `ma-rope` at N=8, there are **35 CSV files for only 5 seeds** (7 per seed) and 30 for N=32
   (6 per seed) — far more than one eval file per seed. `queue_loss` (last row) across these 35
   files at N=8 ranges from **0.0 to 0.158** (mean ≈0.059), which is a huge spread for "the same"
   configuration.
2. Checked file modification timestamps for one seed's files
   (`results/paper_reproduction/n8/ma-rope_seed_0_ep_*_hash_*.{csv,pt}`): they span **2026-07-14
   18:31 through 2026-07-16 10:32** — nearly two full days, in distinct clusters, not one
   contiguous run. Each cluster has its own checkpoint hash, meaning these are **independent
   training-and-eval repeats from different points in the project's history, accumulated in the
   same output directory with no run-ID or campaign separator beyond the content-derived hash.**

This directly violates the mission's Working Rule #9 ("do not mix results from different
campaigns") — and it predates my involvement; it's baked into the existing repository structure.
**This is a much better-supported explanation for the manuscript's queue-loss drift across
versions (1.15% → 0.85% → 2.14%, plus the Fig. 10 mismatch) than any single code bug**: whichever
of these 6-7 overlapping historical runs someone happened to read from at report-writing time
would yield a different "the" queue-loss number for MA-ROPE, entirely independent of any actual
change in the underlying algorithm.

Practical implication for Phase 3/7: none of the existing `results/paper_reproduction/` data can
be trusted as a single clean campaign. It needs to be archived intact (per Working Rule #3 — never
overwrite historical outputs) and a **fresh, single, clearly-labeled campaign** run under the
canonical pipeline (`reproduce_paper_sweeps.py`, `env_mode=baseline_recreation`, fixed seed list,
one code commit/state) before any new queue-loss number can be reported with confidence. This is
the concrete next action.

## 2026-08-02 — Canonical campaign: infrastructure built, fidelity-verified, partially executed

Built `scripts/run_canonical_campaign.py` (new file; does not modify the frozen
`reproduce_paper_sweeps.py`) plus `scripts/generate_canonical_reports.py`. Archived the
pre-existing `results/paper_reproduction/` (140 files, checksums verified identical) to
`archive/history/paper_reproduction_PREEXISTING_20260802T173708Z/` before running anything new.

**Second protocol gap found and fixed at the orchestrator level (disclosed, not silent)**:
neither `train_ma_rope()` nor `D3QNAgent`/`FederatedCoordinator` ever call
`torch.manual_seed()`. All numpy RNG streams (env/coord/agent/replay-buffer) are correctly tied
to the `seed` parameter, but `DuelingQNetwork`'s weight initialization draws from torch's
unseeded global RNG. Verified empirically: three fresh `python3` processes constructing the
identical `DuelingQNetwork(12, 11)` produced three different first-weight values
(-0.2558, -0.1723, -0.0199). This means the original pipeline's network initialization was never
actually reproducible, for any seed, across separate process runs. Since this sandbox forces
MA-ROPE training to run in many separate short-lived processes (see below), I added
`torch.manual_seed(seed)` in the orchestrator's agent/coordinator construction. This changes no
environment, algorithm, or metric formula. Verified the fix + the whole checkpoint/resume
mechanism are bit-identical to an uninterrupted call of the real `train_ma_rope()`: a manually
chunked 1-episode + save/reload + 1-episode run reaches the exact same checkpoint hash, step
count, and FedAvg round count as an uninterrupted 2-episode call, given the same seed.

**Campaign `CAMPAIGN_CANONICAL_20260802`**, `results/CAMPAIGN_CANONICAL_20260802/`:
- AllOffload + NoOffload: all 30 combinations (N=8/16/32 x 5 seeds x 2 methods) genuinely
  executed and recorded — no training required, ~0.5-2s each.
- MA-ROPE: measured real per-episode training cost directly — N=8 ≈18.4s/episode, N=16
  ≈25.8s/episode, **N=32 exceeds 42s for a single episode** (measured by direct timeout). This
  sandbox's shell tool caps every command at ~45s with no persistent background processes
  between calls. The checkpoint/resume trainer checkpoints at episode boundaries, so it can make
  incremental progress at N=8 (~2 episodes/call) and N=16 (~1 episode/call), but **N=32 cannot
  make any progress at all under this design** — a single episode alone doesn't fit in one call.
  Fixing that needs step-level (mid-episode) checkpointing, which serializes env internal state
  (positions/speeds/tasks/queues) mid-episode — not yet built.
- Real progress so far: `ma-rope_n8_seed0` has 2/100 episodes done (checkpointed, resumable,
  genuinely trained, not fabricated).
- `CANONICAL_CAMPAIGN_MANIFEST.json`, `CANONICAL_BASELINE_RESULTS.csv`,
  `CANONICAL_BASELINE_REPORT.md` generated reflecting this exact partial state (30/45 complete,
  1 in progress, 14 not started) — no placeholder or interpolated rows for incomplete combos.

**Practical implication**: completing all 15 MA-ROPE combinations (N=8/16/32 x 5 seeds x 100
episodes) via one-episode-or-so-per-tool-call chunking in this sandbox would take on the order of
~750+ more chunked calls for N=8/N=16 alone, and N=32 cannot proceed at all without further
engineering (step-level checkpointing) or different execution hardware. Flagged to the user as a
resourcing decision, not something to silently work around by reducing episode count (would
violate "do not tune parameters") or by silently switching environments.

## Not yet investigated (open, carried into Phase 2/4 continuation)

- Whether the `is_new_task` bug (root cause #1) is sufficient on its own to explain the full
  observed range of queue-loss values (1.15% / 0.85% / 2.14% / 38.0% / 1.3%), or whether other
  factors (different `mode` settings, different episode counts per run, the energy-formula
  variants also gated by `mode`) compound it. Needs a controlled experiment: run the same
  scenario with and without the fix, across several seeds, and compare aggregate queue-loss.
- RESOLVED (2026-08-02): re-checked the parameter-count question directly against the real
  `agents/d3qn/network.py` with the real dims (`state_dim=12, action_dim=11`):
  `sum(p.numel() for p in net.parameters())` = 136,460, confirming my earlier approximation. But a
  grep across every `.tex` file in `MA_ROPE/MASTER/MA_ROPE_MASTER_v21/` for "50k", "50,000", any
  k-parameter phrasing, or "Table XIV" found **no matching claim anywhere in the current
  manuscript source**. I cannot verify this discrepancy exists in the document as it currently
  stands, so I'm dropping it rather than reporting an unverified claim. (It may have been in an
  earlier draft, a Word-based audit doc, or my own misremembering from earlier in this
  engagement — not confirmed either way.)

## 2026-08-03: Path B correction pipeline built, fidelity-verified, and handed off

Per the 7-point correction plan (following `QUEUE_LOSS_ROOT_CAUSE_REPORT.md`'s "mixed causes"
verdict and Path B recommendation):

- Built `scripts/run_corrected_campaign.py` (sibling of, not a replacement for,
  `run_canonical_campaign.py` — Path A's `CAMPAIGN_CANONICAL_20260802` remains untouched). Two
  concrete fixes, no environment/algorithm/hyperparameter changes: (1) `queue_loss` renamed to
  `conditional_tx_failure_rate` with identical computation, plus new `fleet_tx_failure_rate` and
  absolute counts, via a new `evaluate_policy_v2()`; (2) the final MA-ROPE checkpoint now persists
  **all N agents'** `online_net` state_dicts (`all_agent_online_net_state_dicts`), not just agent
  0's — closing the gap documented in the root-cause report's §2 fidelity caveat.
- Extended `verify_chunk_fidelity()`'s `--verify-fidelity` entry point with a second, new check,
  `verify_all_agent_checkpoint_persistence()`: trains a small (n_agents=3) fixture for 2 real
  episodes, confirms `update_count > 0` (so the check can't trivially pass on an untrained,
  coincidentally-identical network), then verifies the final `.pt`'s
  `all_agent_online_net_state_dicts` has exactly `n_agents` entries and each is byte-identical
  (`torch.equal` per tensor) to that agent's live in-memory weights. **Ran for real in this
  sandbox — both checks passed**: `chunk-resume fidelity=PASS` (inherited unchanged from Path A,
  bit-identical hash/step_count/fedavg_rounds), `all-agent checkpoint persistence=PASS`
  (`n_agents=3, saved_agents=3`, exact match, `any_agent_learned_update=True`). Full console
  output captured in this session; exit code 0.
- One test fixture artifact (`results/corrected_v2_staging/n3/ma-rope_seed_998_ep_2_hash_a6d7a2a1.pt`)
  could not be deleted afterward — same sandbox file-deletion permission quirk documented earlier
  in this log. Harmless: `n=3, seed=998` never collides with the real campaign grid
  (`n∈{8,16,32}`, `seed∈{0..4}`), and the whole `results/corrected_v2_staging/` directory is
  intermediate staging, not a reportable result.
- Built `scripts/generate_corrected_reports.py` (sibling of `generate_canonical_reports.py`,
  producing `CORRECTED_*` files, never `CANONICAL_*`, so the two report families can't be
  confused). Smoke-tested against a synthetic one-row manifest in `/tmp` before being trusted —
  ran cleanly, produced correct CSV/JSON/MD output, cleaned up afterward.
- Wrote `EXECUTION_CONTRACT_V2.md`: handoff spec for the fresh, uncontaminated 5-seed Path B
  campaign (`CAMPAIGN_CORRECTED_20260803`), mirroring `EXECUTION_CONTRACT.md`'s structure —
  exact command, config, checkpoint policy, output schema, and an 11-point pass/fail checklist
  (extends Path A's 9 with two Path-B-specific checks: all-agent checkpoint entry count, and a
  cross-check that static-policy metrics match Path A exactly since those methods involve no
  training randomness). **Campaign has not been run yet** — this is the handoff artifact per the
  user's standing instruction that expensive execution happens off-sandbox.
- Wrote `MANUSCRIPT_IMPACT_MEMO.md` (correction-plan item 7). Explicitly separates two issue
  classes: (1) the queue-loss claim, which Path B directly targets and for which corrected
  replacement language is drafted (pending real campaign numbers), and (2) the much larger
  headline-table mismatch documented in `MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md` (U_PRR, U_OTR,
  Energy, Latency all showing Category D/E divergence from the manuscript, not just queue-loss) —
  explicitly flagged as **not addressed by anything in the 7-point plan** and requiring its own
  Phase 6 path decision (re-baseline the whole headline table vs. explicitly scope the paper to a
  documented earlier model version). Memo does not touch the manuscript and recommends against
  sending any version to the professor until the fresh campaign's numbers are in and the broader
  path decision is made.

**Not yet done**: the actual `CAMPAIGN_CORRECTED_20260803` execution (needs to go to
Antigravity/local machine per `EXECUTION_CONTRACT_V2.md`), and the Issue-class-2 path decision
(Phase 6, still open, larger in scope than Path B).

## 2026-08-03: Scientific decision phase — position/publication/roadmap/briefing documents

Produced four PI-level documents (no code or manuscript changes): `SCIENTIFIC_POSITION_REPORT.md`
(every major finding across 11 areas classified confirmed/disproved/partially-confirmed/replaced,
with evidence citations), `PUBLICATION_DECISION.md` (AE-level verdict: reject as-is, conditional
major-revision path via Tier 1/2/3 scientific work; recommendation to pursue Corrected MA-ROPE, not
MA-ROPE++, since the root-cause investigation never showed the algorithm itself broken),
`RESEARCH_ROADMAP.md` (Path B scientific story: title/hypothesis/contributions/evidence/reviewer
risks, plus a sequenced Tier 1→2→3 plan with dependencies), `PROFESSOR_BRIEFING.md` (one page,
plain language, no audit/engineering jargon).

## 2026-08-03: Non-trivial baseline implemented (UCB-RAT, Wu2021-inspired reconstruction) + training-duration diagnostic built

Following the correction plan's items 2 and 3 (add a real baseline; run a training-duration
diagnostic to resolve whether MA-ROPE's WiFi6 over-reliance is a converged tradeoff or an
undertraining artifact):

- **Investigated Wu2021 feasibility first, per Working Rule (never fabricate)**: the manuscript
  (`references.bib`) cites Wu2021 with a title/venue only, zero equations/pseudocode anywhere.
  `experiments.tex` glosses it as "4-arm stateless bandit"; `related_work.tex` Table I marks it
  Multi-RAT=NO, Partial-ρ=NO, FL-Privacy=NO — a faithful, certifiable reproduction is not possible
  from what's recovered. **New finding, larger than previously scoped**: `experiments.tex` line 16
  actually names FIVE unimplemented comparator baselines (MADDPG, CoopEC-Shao2025, UCB-Wu2021,
  Lyapunov-Jing2019, GA+DQN-Yun2022), not just Wu2021 — flagged in `EXECUTION_CONTRACT_V3.md` §0 as
  a larger open item than `PUBLICATION_DECISION.md` Tier 1 item 4 previously scoped; not resolved
  here, only the one instructed baseline was implemented.
- **Implemented a disclosed reconstruction, not a claimed faithful reproduction**: a stateless UCB1
  bandit (classic Auer et al. 2002 formula) over 4 arms consistent with Wu2021's own feature-table
  properties: `{Local, 5G-NR@25%, 5G-NR@50%, 5G-NR@100%}` (`ACTION_MAP` entries 0/6/7/8), one
  independent bandit instance per vehicle (no cross-vehicle coordination, matching FL-Privacy=NO),
  learning online across the 5 eval episodes (state persists across episodes, only the environment
  resets). Added to `scripts/run_corrected_campaign.py` as `policy_type="ucb_bandit"`, wired into
  `STATIC_POLICIES` and the default `methods` tuple (campaign is now 60 combinations, not 45).
  **Must be labeled "UCB-RAT (Wu2021-inspired reconstruction)" everywhere reported, never "Wu2021"
  unqualified** — full rationale documented inline next to the `UCB_ARMS` constant.
- **Smoke-tested for real, not just written**: ran `evaluate_policy_v2(..., "ucb_bandit", n=8, ...)`
  standalone (exit 0, plausible non-degenerate metrics) and a second diagnostic run tracking
  per-vehicle arm-pull counts and per-arm mean reward directly — confirms the bandit correctly
  learns to prefer the empirically higher-reward arm (Local, mean reward ≈0.97) while still
  exploring the others per UCB1's guarantee, not stuck or degenerate.
- **Training-duration diagnostic**: built `scripts/run_training_duration_diagnostic.py` (new,
  separate from the main campaign — own resume-state and output directory, never mixed). Trains
  MA-ROPE to sequential checkpoints (100→250→500 episodes by default) reusing
  `train_ma_rope_resumable()`/`evaluate_policy_v2()` unmodified. Extended `evaluate_policy_v2()`
  with an opt-in `track_actions=False` parameter (default unchanged, zero effect on the
  already-contracted CSV schema when left False) that tallies action distribution, per-RAT usage,
  and mean realised ρ — needed for this diagnostic, generically useful beyond it.
  **Smoke-tested end to end** with a tiny fixture (n=2, seed=995, checkpoints 1/2/3): confirmed
  sequential resume correctly continues training (`step_count` 100→200→300, `fedavg_rounds`
  2→4→6, matching 100 steps/episode and sync-every-50), confirmed `track_actions=True` returns
  correct, internally-consistent action/RAT distributions, confirmed CSV/manifest/`EXECUTION_REPORT.md`
  generation all work. Exit code 0.
- Wrote `EXECUTION_CONTRACT_V3.md`, superseding V2 for the campaign (now 4 methods/60 combos) and
  adding the training-duration diagnostic as a second, separate deliverable — both with their own
  validation checklists, both still pending real execution on unconstrained hardware.
- Two more small test-fixture artifacts could not be deleted afterward (same sandbox permission
  quirk documented earlier): `results/corrected_v2_staging/n8/ucb_bandit_seed_777_ep_5_hash_none.csv`
  and everything under `results/_TEST_DURATION_DIAG/`. Both harmless — neither's naming (seed 777,
  seed 995, diagnostic-id `_TEST_DURATION_DIAG`) can ever collide with the real campaign grid or
  the real diagnostic ID (`CAMPAIGN_TRAINING_DURATION_20260803`).

**Not yet done**: actual execution of either deliverable in `EXECUTION_CONTRACT_V3.md` on
unconstrained hardware; the Issue-class-2 path decision (still open); the broader 5-baseline gap
just discovered (not addressed, only disclosed).

## 2026-08-03: AG executed both EXECUTION_CONTRACT_V3.md deliverables — independently validated, both PASS

AG reported completion of `CAMPAIGN_CORRECTED_20260803` (60/60 combos) and
`CAMPAIGN_TRAINING_DURATION_20260803` (3/3 checkpoints). Per standing methodology, did not accept
the self-report at face value — re-verified independently from the actual files on disk:

**Corrected campaign — all checks passed:**
- Recomputed `compute_code_hash()` from local `env/`/`agents/` files: exact match to the manifest's
  recorded `code_hash_sha256` (`3050d0c2...`).
- 60/60 combos present, exact 4-method × 3-density × 5-seed grid (`Counter` over the CSV confirms
  no missing/duplicate cells).
- Structural invariants: 0 `nooffload` rows with nonzero `conditional_tx_failure_rate`; 0 `ma-rope`
  rows deviating from `step_count=10000, fedavg_rounds=200`.
- **Cross-campaign determinism check**: `alloffload`/`nooffload` `conditional_tx_failure_rate` in
  this campaign matches Path A's (`CAMPAIGN_CANONICAL_20260802`) `queue_loss` **exactly** (0
  mismatches across all 30 static-policy rows) — expected since these are deterministic given fixed
  seeds, and confirms no code drift between the two campaigns.
- All 15 `ma-rope` checkpoints: recomputed `get_checkpoint_hash()` from the actual `.pt` file bytes
  matches the manifest's recorded hash for every file; every file's
  `all_agent_online_net_state_dicts` has exactly `n_agents` entries (32/16/8 as expected) — the
  Path B checkpoint fix genuinely shipped in the real campaign, not just the earlier small fixture.
- **UCB-RAT baseline validated by independent re-execution, not just inspection**: re-ran
  `evaluate_policy_v2(..., "ucb_bandit", n=32, seed=0, ...)` myself from scratch and got
  `conditional_tx_failure_rate = 0.024221345937865797`, matching the manifest's recorded value to
  15 significant digits — about as strong a validation signal as is available short of a bit-exact
  file diff. Also confirmed the action distribution uses only `{0, 6, 7, 8}` (the declared 4-arm
  set) with zero uses of any other action.
- **Bug found and fixed (mine, not AG's)**: the campaign's `wu2021_status` manifest field still said
  "NOT INCLUDED" — stale text written before the UCB-RAT baseline was added, never updated. Fixed
  `_load_or_init_manifest()`'s source text for future campaigns, and patched the two existing
  manifest JSON files for this already-completed campaign in place (metadata only, no numeric
  result touched), then regenerated `CORRECTED_BASELINE_REPORT.md` — confirmed 60 rows and code
  hash unchanged after the patch, only the status text corrected.

**Training-duration diagnostic — all checks passed:**
- `step_count`/`fedavg_rounds` arithmetic exactly correct at all three checkpoints (10000/200,
  25000/500, 50000/1000 for 100/250/500 episodes).
- All three `.pt` checkpoints: hash recomputed correctly, all 32 agent entries present.
- **Ruled out the most concerning failure mode directly**: confirmed the three checkpoints are
  genuinely different networks (`torch.equal` on first-layer weights returns `False` for all three
  pairwise comparisons) — the sequential resume mechanism produced real, continued training between
  stages, not a stalled/no-op resume reporting fabricated progress.
- Training duration scales consistently with cumulative episode count (287.6s→726.4s→1452.6s for
  100/250/500 episodes) — linear-ish scaling as expected for genuine continued training, not a
  shortcut.
- `action_distribution_json`/`rat_usage_json` sum to `total_vehicle_steps_total=16000` exactly at
  all three checkpoints.

**Finding (data-level, disclosed with an interpretive caveat, not yet a manuscript claim)**: across
100→250→500 episodes (5x more training), MA-ROPE's aggregate behavior at N=32/seed=0 barely moves —
`conditional_tx_failure_rate` 5.91%/6.03%/5.92%, `fleet_otr` 0.906/0.903/0.884, RAT usage
essentially flat (WiFi6: 186/171/185 out of 16,000 vehicle-steps). Important caveat before this gets
over-read as "proof of full convergence": `evaluate_policy_v2()`'s eval protocol always resets the
environment with the identical seed offsets (`seed+100+ep`) regardless of how long training ran, so
the underlying environment randomness (channel fading draws, task arrivals) replays identically
across all three checkpoints' evaluations — only the policy's decisions can differ, and only a small
fraction of the 16,000 vehicle-steps are ones where a differently-trained policy could plausibly
choose differently. The flatness is genuine (not a bug — proven by the checkpoint-divergence check
above) but reflects "no material behavioral change from more training, on this one seed," not
necessarily "the policy has converged in a stronger sense." **Recommend expanding to at least 2-3
more seeds before treating this as a settled answer to the Path B vs. Path C question** — this is
exactly the kind of judgment call `EXECUTION_CONTRACT_V3.md` §3 reserved for a reviewing scientist
rather than automatic expansion.

**Cross-campaign determinism check, extended to MA-ROPE itself (not just the static policies)**:
compared checkpoint hashes for all 15 `ma-rope` combos between Path A and Path B. **14/15 are
bit-identical** (exact same checkpoint hash, same every downstream metric to full float precision)
despite being two fully independent campaign executions — strong, direct evidence the training
pipeline is genuinely deterministic given a fixed seed, across separate runs, not just within one
process. **Exactly one combo diverges: `ma-rope_n8_seed0`** (hash `e0a1c45e` in Path A vs. `6fb651de`
in Path B). Root cause identified, not left as a mystery: per this log's own 2026-08-02 entry, Path
A's `ma-rope_n8_seed0` was the ONE combo I had personally trained 2/100 episodes of, myself, in this
sandbox, before handing the remainder off to AG for completion — meaning Path A's checkpoint for
that one cell resulted from resuming across two different execution environments (this sandbox, then
AG's machine), while every other combo (including all of N=16/N=32) trained entirely within AG's
single environment for both campaigns. Path B's `CAMPAIGN_CORRECTED_20260803` was a brand-new
campaign with no pre-existing partial checkpoint, so its `ma-rope_n8_seed0` trained fully within
AG's environment end to end — making it arguably the MORE trustworthy of the two values for that one
cell, not a regression. This does not affect N=16 or N=32 (the primary headline density) at all, and
does not weaken the overall reproducibility finding — if anything, 14/15 exact cross-execution
matches is stronger evidence of determinism than anything checked before this point.

## 2026-08-03: Workstreams 1-2 (Energy, baselines) — Energy verdict REMOVE; baseline table integrity finding

Per the endorsed post-validation plan (freeze everything except Energy, baselines, claim audit):

- **Energy (`ENERGY_METRIC_DECISION.md`)**: traced the defect to its exact source.
  `env/environment.py`'s `baseline_recreation`/`legacy_guide` energy formula (the ONLY mode this
  entire reproduction has ever used) is not a unit-conversion bug as previously characterized — it's
  a dimensionally invalid formula (`P_CPU_W * log10(fraction)` for local-only tasks, which is
  negative by construction for the common case; the code's own comment calls it a "literal rendering
  formula," not a physics-derived one). The existing `energy_si_corrected` mJ->J fix
  (`ENERGY_UNIT_IMPACT_REPORT.md`) lives in a completely different code branch (`else`, for
  non-canonical modes) that `baseline_recreation` never reaches — it's dead code for every result
  this reproduction has produced. **Verdict: REMOVE Energy from reporting**, not fixable within
  current scope without either inventing a new formula or switching simulator modes entirely (both
  out of scope per the standing "do not redesign the simulator" instruction).
- **Baseline feasibility (`BASELINE_TABLE_INTEGRITY_FINDING.md`) — escalated beyond a scoping
  question.** Investigating MADDPG/CoopEC-Shao2025/Lyapunov-Jing2019/GA+DQN-Yun2022 surfaced that
  **10 of 12 rows in the manuscript's headline `full_performance` table share an identical Fleet OTR
  value (0.8340) to four decimal places — including MA-ROPE's own row.** Closer inspection found
  `Jing2019` and `Shao2025` are byte-identical across *all five* reported columns, and a separate
  table reports `Wu2021`'s safety-task numbers as identical to MA-ROPE's own row. Only
  AllOffload/NoOffload (independently known to be genuinely, deterministically computed) differ.
  This is evidence-based, not an intent claim — the finding is that these rows show a pattern
  inconsistent with independently-executed experiments, not a claim about why. **This supersedes the
  original "missing baseline" framing**: there is no credible target in the current table to
  reproduce against, for any of the four algorithms. Recommendation: narrow the paper's comparison
  set to what's genuinely implemented and validated (MA-ROPE, AllOffload, NoOffload, UCB-RAT), or
  scope any of the four as genuinely new future work — not a decision made unilaterally here, since
  it's a scope/resourcing call for Vivek and the professor.

**UCB-RAT baseline results (N=32, mean±std over 5 seeds), for context**: U_PRR 0.899±0.002 vs.
MA-ROPE's 0.958±0.001; Fleet OTR 0.346±0.005 vs. MA-ROPE's 0.888±0.014; fleet_tx_failure_rate
1.41%±0.04% vs. MA-ROPE's 0.24%±0.03% (MA-ROPE causes ~6x fewer absolute fleet-wide failures than
this baseline too, not just vs. AllOffload); `conditional_tx_failure_rate` 2.54%±0.08% vs.
MA-ROPE's 5.46%±0.68% (same per-attempt-vs-absolute pattern as the AllOffload comparison, for the
same disclosed reason). MA-ROPE decisively beats this non-trivial baseline on every metric except
the per-attempt conditional rate. See `CORRECTED_RESULT_TABLES.md` for the full table.

## 2026-08-03: Mixed baseline decision executed — CoopEC-RAT implemented, MADDPG/GA+DQN dropped, Lyapunov queued

User's decision on the baseline-scope question (per `BASELINE_TABLE_INTEGRITY_FINDING.md`): "mix"
of narrowing the table and implementing 1-2 as real future work. Executed:

- **Implemented `coopec_greedy`** ("CoopEC-RAT," disclosed reconstruction, not a reproduction) in
  `scripts/run_corrected_campaign.py`: a hand-crafted, non-learned, single-RAT (5G-NR), binary
  offload rule using only task properties (offload if local compute latency would exceed 50% of the
  task's deadline; else compute locally) — deliberately excludes channel/queue state, per
  `related_work.tex`'s own description of CoopEC as unable to "adapt to channel dynamics or queue
  contention." Chosen as the single most tractable of the four remaining baselines (a hand-crafted
  scoring rule, unlike MADDPG's multi-agent actor-critic or GA+DQN's genetic-algorithm wrapper).
  Smoke-tested standalone before trusting it (sane, non-degenerate: 2302/16000 offload decisions at
  N=32 seed 0, plausible metrics).
- **Extended the existing campaign idempotently**, not from scratch: re-invoked `run_campaign()` on
  the already-complete `CAMPAIGN_CORRECTED_20260803` directory with `coopec_greedy` added to
  `methods` — it correctly skipped all 60 already-complete combos and computed only the 15 new
  `coopec_greedy` cells (no MA-ROPE retraining needed, since this is a zero-training static policy).
  Campaign is now 75/75 complete; code hash unchanged (`3050d0c2...`, orchestrator files were never
  part of that hash, consistent with Path A's original design).
- **Result**: CoopEC-RAT is the most competitive alternative found so far — Fleet OTR 0.801±0.004 at
  N=32 (behind MA-ROPE's 0.888, ahead of UCB-RAT's 0.346 and AllOffload's 0.125), and its
  `conditional_tx_failure_rate` (2.30%±0.02%) is the *lowest* of any offloading policy in the table,
  including MA-ROPE's. Degrades gently with density (0.903→0.823→0.801, N=8/16/32) since its
  decision rule has no queue/channel dependence by design.
- **MADDPG and GA+DQN-Yun2022**: dropped from the comparison table entirely, per decision — no
  credible target existed to reproduce or compare against.
- **Lyapunov-Jing2019**: queued as a future-work candidate, not implemented this round, to keep
  CoopEC's implementation properly scoped and verified rather than rushing two at once.
- Updated `CORRECTED_RESULT_TABLES.md`, `CLAIM_BY_CLAIM_MANUSCRIPT_IMPACT.md`, and
  `GO_NO_GO_DECISION.md` to reflect the resolved decision on both Energy and the baseline gap — of
  the original three post-validation blockers, two are now resolved (Energy: remove; baselines:
  CoopEC-RAT added, MADDPG/GA+DQN dropped, Lyapunov queued) and one remains open (training-duration
  diagnostic seed expansion).

## 2026-08-03: Training-duration diagnostic expanded to 3 seeds; real concurrency bug found and fixed

AG ran seeds 1 and 2 (N=32, checkpoints 100/250/500) concurrently in the background, per the handed
prompt. Validated the same way as everything else — not accepted at face value:

- All 9 checkpoints (3 seeds x 3 durations) independently re-verified directly from the CSV +
  checkpoint files: `get_checkpoint_hash()` recomputed matches every reported hash, every `.pt` has
  exactly 32 agent entries, `step_count`/`fedavg_rounds` arithmetic exact for every row, and all 9
  checkpoints are pairwise genuinely distinct (`torch.equal` on first-layer weights is `False` for
  every pair, not just within a seed).
- **Bug caught, not assumed away**: `manifest.json` was missing all three of seed 1's entries, even
  though AG's own message claimed it "correctly contains the metadata for all 9 files" (a claim that
  turned out to be false — exactly why nothing here is accepted on a self-report). Root cause: seed 1
  and seed 2 ran as concurrent background processes against the same diagnostic-id; each held its own
  in-memory manifest loaded at start, and the read-modify-write save pattern meant whichever process
  finished last silently overwrote the other's already-written keys. The CSV was unaffected (it's
  append-only). Recovered the three missing entries by reconstructing them from the independently
  verified CSV rows and checkpoint files (not fabricated — every value re-derived from real,
  already-validated sources) and patched `manifest.json` in place.
- **Fixed the underlying bug**, not just the symptom: added `_merge_and_save_manifest()` to
  `scripts/run_training_duration_diagnostic.py` — reloads whatever is currently on disk immediately
  before every write and merges this process's own entries into it, rather than blindly overwriting.
  Not perfectly atomic (a race window remains between reload and write), but eliminates the actual
  failure mode observed, which unfolded over many minutes, not milliseconds. Smoke-tested with a
  simulated concurrent-write race (two in-memory manifests, both starting empty, writing different
  keys in sequence) before trusting it — both processes' entries survived. Regenerated
  `EXECUTION_REPORT.md` from the repaired manifest; all 9 rows now present and correctly grouped.

**Finding, now supported by three seeds instead of one** (`CORRECTED_RESULT_TABLES.md`): the
within-seed effect of 5x more training (100->500 episodes) on `conditional_tx_failure_rate` and Fleet
OTR is the same size as, or smaller than, ordinary cross-seed noise (main campaign's 5-seed std), and
its direction is inconsistent across the three seeds (Fleet OTR goes down for seed 0, up for seed 1,
roughly flat for seed 2) — not the signature of a genuine training-duration effect. This substantially
strengthens (does not just repeat) the earlier single-seed read: MA-ROPE's WiFi6 reliance at N=32
looks like a converged policy characteristic, not an artifact of the standard 100-episode protocol.

**All three of the post-validation blockers identified in `GO_NO_GO_DECISION.md` are now resolved.**
The only remaining step before this can go to the professor as a submission-track draft is actually
drafting the manuscript revisions (Phase 8/9) — not fixed by more data or more decisions, since none
remain open.
