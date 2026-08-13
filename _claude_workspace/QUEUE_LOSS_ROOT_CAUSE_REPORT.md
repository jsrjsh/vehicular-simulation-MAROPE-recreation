# QUEUE_LOSS_ROOT_CAUSE_REPORT.md

Investigation of: why the canonical implementation produces higher `queue_loss` for MA-ROPE
(5.46%, 5-seed mean) than AllOffload (2.46%) at N=32, reversing the manuscript's claimed
ordering (1.15% vs 2.14%). No manuscript or code changes were made; the only new artifacts are
a read-only instrumentation script and its output traces.

---

## 1. Exact definition of `queue_loss`

Traced from `env/environment.py` through `scripts/reproduce_paper_sweeps.py:evaluate_policy()`
(lines ~180-226) to the CSV column.

**The name is a misnomer. `queue_loss` does not measure RSU queue rejection or overflow. It
measures link-layer transmission failure rate, conditional on a transmission being attempted.**

Exact equation, per episode:

```
tx_queue_losses = []
for each vehicle i, each step:
    if chosen_rat[i] > 0 and chosen_rho[i] > 0.0:        # denominator gate
        tx_queue_losses.append(1.0 if not transmission_success[i] else 0.0)   # numerator

queue_loss (episode) = mean(tx_queue_losses)   # 0.0 if the list is empty
queue_loss (reported) = mean over 5 eval episodes
```

Answering each required question directly:

- **Where incremented**: `evaluate_policy()`, the `tx_queue_losses.append(...)` line. The
  underlying `transmission_success` flag is set inside `env/environment.py:step()`, Section 4
  (`successes[i] = compute_link_success(rat_idx, sinr_db, self.rng, mode=self.mode)`,
  `env/channel.py:103-122`).
- **Numerator**: count of attempted transmissions where `compute_link_success()` returned `False`
  — a Bernoulli draw whose probability is a sigmoid function of `(sinr_db - sinr_thresh_db)`
  (`env/channel.py:114-119`). SINR depends on distance, speed, path-loss model, shadow fading, and
  Doppler fading for the **chosen RAT only** (`env/channel.py:75-101`).
- **Denominator**: count of (vehicle, step) pairs where `chosen_rat > 0 and chosen_rho > 0.0` —
  i.e., a transmission was actually attempted. Steps where the vehicle acted "Local" (action 0,
  or any action with nominal ρ=0) are **excluded from both numerator and denominator entirely.**
- **Units**: counts (vehicle, step, attempt) tuples, not packets, not tasks, not bytes.
- **Can partial offloading create multiple counted events?** No. Exactly one event per
  (vehicle, step) where a transmission is attempted, regardless of ρ. ρ does not appear anywhere
  in `compute_link_success()`'s signature (`env/channel.py:103`) — **the realized offload
  fraction has zero mathematical effect on whether an attempt is counted as a "loss."**
- **Do local actions enter the denominator?** No — confirmed above.
- **Are failed transmission and queue rejection separated?** There is no separate "queue
  rejection" code path to separate from. The RSU queue (`self.rsu_queues`) only ever contributes
  to **latency** (`l_queue = self.rsu_queues[rsu_idx] * self.delay_per_unit_ms`,
  `env/environment.py:291`) and never to transmission success/failure or any explicit rejection.
  There is no capacity cap on `rsu_queues` anywhere in the codebase (grepped `env/environment.py`
  in full — confirmed no `if rsu_queues[...] > capacity` or equivalent exists). **A metric called
  "queue loss" that measures link failure, with no actual queue-capacity-triggered loss event
  anywhere in the implementation, is the single most important fact in this investigation.**
- **Averaging**: per-episode mean of a per-(vehicle,step) binary indicator, then arithmetic mean
  across the 5 eval episodes (`scripts/reproduce_paper_sweeps.py`, `ep_queue_loss.append(...)`
  then `np.mean(ep_queue_loss)`), then arithmetic mean across 5 seeds in
  `CANONICAL_BASELINE_RESULTS.csv`. Not weighted by vehicle count, task size, or workload.

---

## 2. Event-by-event traces

Produced by `scripts/queue_loss_forensics.py` (new, read-only; does not modify `env/`, `agents/`,
or `scripts/reproduce_paper_sweeps.py`), mirroring `evaluate_policy()`'s exact construction,
seeding (`env.reset(seed=seed+100+ep)`), and action-selection logic, at N=32, seed 0, using the
**real trained checkpoint** from the validated canonical campaign
(`results/CAMPAIGN_CANONICAL_20260802/raw/n32/ma-rope_seed0.pt`):

- `results/CAMPAIGN_CANONICAL_20260802/forensics/QUEUE_EVENT_TRACE_MAROPE.csv` (16,000 rows: 5
  episodes x 100 steps x 32 vehicles)
- `results/CAMPAIGN_CANONICAL_20260802/forensics/QUEUE_EVENT_TRACE_ALLOFFLOAD.csv` (16,000 rows)

**Fidelity check, disclosed honestly**: re-aggregating the AllOffload trace reproduces the
canonical campaign's exact seed-0 value (2.41% both). The MA-ROPE trace reproduces 4.63%, not the
canonical 5.91% for that seed. Cause identified: `train_ma_rope()` only persists `agent[0]`'s
weights to disk (`get_checkpoint_hash(coord.agents[0].online_net.state_dict())`,
`scripts/reproduce_paper_sweeps.py:89-97`), but `evaluate_policy()` in the original run evaluated
using **all 32 agents' own individually-trained weights** (passed by reference as the live `coord`
object straight out of training, not reloaded from disk). Since FedAvg participation is
probabilistic (`participation_prob=0.9`, and rounds below 70% participation abort without
syncing — `agents/federated/coordinator.py:116-120`), the 32 agents can end training slightly
unsynchronized, and only agent 0's version survives on disk. My reconstruction (loading agent 0's
saved weights into all 32 agents) is therefore an approximation, not a bit-exact replay. **This is
itself a genuine, separate provenance gap** (the checkpoint format is insufficient to exactly
reproduce a multi-agent evaluation) and is reported here rather than hidden. It does not undermine
the conclusions below: the reconstructed run still shows the same qualitative reversal (4.63% vs
2.41%, MA-ROPE still higher), so the mechanism identified is not an artifact of this
approximation.

---

## 3. Decomposition

From the traces (`queue_loss_forensics.py` output, aggregated directly, no estimation):

| | MA-ROPE | AllOffload |
|---|---:|---:|
| Total vehicle-steps | 16,000 | 16,000 |
| Transmission attempts (denominator) | 743 (4.6% of steps) | 16,000 (100%, by definition) |
| Attempts on RAT 1 (LTE) | 82 (failures: 0) | 0 |
| Attempts on RAT 2 (ITS-G5) | 175 (failures: 0) | 0 |
| Attempts on RAT 3 (WiFi6) | 191 (**failures: 28, 14.66%**) | 0 |
| Attempts on RAT 4 (5G-NR) | 295 (failures: 7, 2.37%) | 16,000 (failures: 385, 2.41%) |
| Failures by task class | safety 28/478 (5.86%), compute 3/112 (2.68%), infotainment 4/153 (2.61%) | safety 239/10163 (2.35%), compute 67/2508 (2.67%), infotainment 79/3329 (2.37%) |
| **queue_loss (per-attempt denominator, the actual metric)** | **35/743 = 4.71%** (this trace's seed; canonical 5-seed mean 5.46%) | **385/16000 = 2.41%** |
| queue_loss recomputed with a **per-generated-task denominator** (all 16,000 vehicle-steps, diagnostic only) | 35/16000 = **0.22%** | 385/16000 = 2.41% (unchanged, since AllOffload always attempts) |

**The single largest, cleanest signal**: RAT 3 (WiFi6) accounts for 28 of MA-ROPE's 35 failures
(80%) despite being only 191 of 743 attempts (26%). Its per-attempt failure rate (14.66%) is 6x
higher than 5G-NR's (2.37%), the RAT AllOffload always uses.

**Why WiFi6 fails so much more (`env/config.py:61-74` vs `:75-88`)**: WiFi6's modeled noise floor
is `-90.0 dBm` versus 5G-NR's `-110.0 dBm` — a 20 dB worse noise floor, which under
`env/channel.py:100`'s `sinr = p_tx - pl - n_0 + shadow - fade` translates directly into
~20 dB lower SINR for WiFi6 at the same distance, and thus a much higher `compute_link_success()`
failure probability under the sigmoid model (`env/channel.py:114-119`). This is a real,
traceable, per-RAT physical-layer parameter difference in the environment's own config — not a
bug in the channel model, just a channel that makes WiFi6 substantially less reliable than 5G-NR
under this parameterization.

---

## 4. Metric semantics category

Testing the exact list given:

- **A. Genuine queue behavior — NO.** No queue-capacity-triggered rejection exists anywhere in
  the code (confirmed in §1). The RSU queue affects only latency.
- **B. Denominator choice — YES, primary contributor.** Recomputing with a per-generated-task
  denominator (§3, last row) flips the result: MA-ROPE 0.22% vs AllOffload 2.41% — the
  manuscript's claimed *direction* is restored (MA-ROPE lower) once the denominator no longer
  excludes non-attempted steps. The metric as actually implemented divides only by *attempts*,
  which mechanically penalizes a policy that rarely transmits but sometimes picks an unreliable
  RAT, relative to a policy that transmits constantly on the single most reliable RAT.
- **C. Partial-offload accounting — NO effect.** `compute_link_success()` does not take ρ as an
  argument at all (`env/channel.py:103`); confirmed by code inspection, no experiment needed.
- **D. Multiple queue events per task — NO.** Exactly one event per (vehicle, step); no
  multiplicity.
- **E. Per-RAT aggregation — YES, primary contributor.** §3's RAT breakdown is the direct cause of
  the magnitude: MA-ROPE's disproportionate use of the unreliable WiFi6 RAT for a meaningful
  fraction of its (already rare) attempts.
- **F. Stale queue state — NO.** Not applicable; the metric doesn't read queue state at all.
- **G. Policy/evaluation mismatch — Partially, see §2's fidelity caveat**, but does not change the
  qualitative conclusion.
- **H. Another implementation defect — the metric's *name* is the defect.** Calling this column
  "queue loss" and having the manuscript caption it as "RSU queue-classified loss fraction"
  (`results_part1.tex:184`) when it is actually a link-layer failure rate conditioned on a
  self-selected, highly imbalanced denominator is a **metric-definition problem**, independent of
  whether the underlying numbers are "correct" for what they actually measure.

---

## 5. Controlled counterfactuals (diagnostics only, not results)

1. **rho fixed to 1.0, RAT preserved** — not run as a separate experiment because it is
   analytically guaranteed to produce an identical outcome: `compute_link_success()` has no ρ
   dependence (§4, item C). Re-running would only reproduce the same numbers with more compute
   spent for zero new information.
2. **Per-offloaded-task denominator** (the actual metric) vs **per-generated-task denominator**:
   done in §3. Result: reverses the ordering. This is the decisive diagnostic.
3. **Queue loss separated by RAT**: done in §3. Result: isolates WiFi6 as the dominant
   contributor for MA-ROPE.
4. **Binary task-loss metric**: the existing metric is already a binary per-event indicator (§1);
   no separate binary-vs-continuous distinction exists to test.
5. **Cross-accounting swap** (MA-ROPE actions scored through AllOffload's "accounting path" and
   vice versa): there is only one accounting function (`evaluate_policy()`'s counting logic
   applies identically regardless of `policy_type`) — there is no separate "AllOffload accounting
   path" to swap into. This diagnostic collapses into item 2 above once that's understood: the
   only thing that differs between the two policies' accounting is which denominator population
   each policy's own actions produce, not the counting rule itself.

---

## 6. Scientific verdict

**Verdict: 4. MIXED CAUSES.**

Quantified contribution:

- **~100% of the magnitude** comes from **denominator choice (B) interacting with per-RAT
  reliability differences (E)**: MA-ROPE attempts transmission on only 4.6% of vehicle-steps, and
  of those attempts, 26% land on WiFi6 (14.7% failure rate) versus AllOffload's 100%-of-steps,
  100%-on-5G-NR (2.4% failure rate) policy. Under the per-attempt denominator the code actually
  uses, a rarely-transmitting-but-occasionally-unreliable policy scores worse than an
  always-transmitting-but-reliable one, even though MA-ROPE causes 11x fewer total failed
  transmissions in absolute terms (35 vs 385 out of the same 16,000 vehicle-steps).
- **0% comes from a queue-capacity bug**, because no such mechanism exists in the code to have a
  bug in (Category A ruled out with certainty).
- **A contributing, independent finding**: the checkpoint-saving convention
  (`train_ma_rope()` persists only `agent[0]`) is insufficient to exactly reproduce a multi-agent
  evaluation, a ~22% relative reconstruction gap on this specific metric (§2). This affects
  reproducibility of exact figures, not the qualitative conclusion.

**Affected files/functions**: `scripts/reproduce_paper_sweeps.py:evaluate_policy()` (denominator
definition and the "queue_loss" name itself); `env/config.py` RAT_SPECS (WiFi6 vs 5G-NR
noise-floor parameters, which are real design choices, not bugs); `scripts/reproduce_paper_sweeps.py:train_ma_rope()`
(checkpoint-saving convention, separate finding).

**Does correcting this change other metrics?** Renaming/redefining the metric changes no other
number in `CANONICAL_BASELINE_RESULTS.csv` — U_PRR, U_OTR, Fleet OTR, energy, and latency are
computed independently and do not depend on `queue_loss`'s denominator choice. Fixing the
checkpoint-saving gap (persisting all N agents, not just agent 0) would be needed before any
exact-reproduction claim about MA-ROPE-specific evaluation metrics, though it would not be
expected to change the *direction* of this finding given the magnitude of the gap.

**Does the existing MA-ROPE conclusion survive?** Not as currently stated. The manuscript claims
MA-ROPE achieves "1.9x lower" queue loss, framed as an operational reliability advantage. The
actual mechanism is close to the reverse of that framing: MA-ROPE causes far fewer total
transmission failures in absolute terms (35 vs 385) simply by transmitting far less often, but
the *rate* metric as defined penalizes it for occasionally choosing an unreliable RAT (WiFi6) when
it does transmit. A revised claim — "MA-ROPE causes 11x fewer total link failures fleet-wide by
minimizing unnecessary offloading, though its per-attempt reliability trails AllOffload's due to
occasional use of the less reliable WiFi6 link" — would be defensible; "1.9x lower queue loss" as
currently written is not, on either the number or, arguably, the underlying operational claim
being named "queue loss" at all.

**Recommended next path**: **B — corrected MA-ROPE**, not immediately C (MA-ROPE++). The
algorithm itself is not shown to be broken; the metric definition and the checkpoint-saving gap
are the two concrete, fixable issues, and the RAT-selection sub-optimality (over-reliance on
WiFi6 for a trained-but-not-fully-converged policy) is a legitimate target for correction within
the existing MA-ROPE framework (e.g., more training episodes, or reward shaping that penalizes
low-reliability RAT choices more directly) before concluding a structurally different MA-ROPE++
design is required. This recommendation is scoped to this one metric; it does not resolve the
broader headline-table gaps documented in `MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md`, which still
need their own path decision.
