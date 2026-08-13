# BASELINE_TABLE_INTEGRITY_FINDING.md

Workstream 2 was scoped as "assess feasibility of implementing MADDPG, CoopEC-Shao2025,
Lyapunov-Jing2019, GA+DQN-Yun2022." That investigation surfaced something more serious than a
missing-implementation gap, and it needs to be stated plainly before any baseline-scoping decision
is made: **the manuscript's own reported numbers for every non-trivial comparator show a pattern of
internal duplication inconsistent with independently executed experiments.**

## The evidence, read directly from `results_part1.tex`

**Table `full_performance` (N=32, the paper's headline table), Fleet OTR column:**

| Method | Fleet OTR |
|---|---:|
| MA-ROPE Full | 0.8340 |
| Yun2022 (GA+DQN) | 0.8340 |
| Wu2021 (UCB Bandit) | 0.8340 |
| Jing2019 (Lyapunov) | 0.8340 |
| Shao2025 (CoopEC) | 0.8340 |
| DQN — Shao constraints | 0.8340 |
| DQN — Yun constraints | 0.8340 |
| DQN — Wu constraints | 0.8340 |
| DQN — Jing constraints | 0.8340 |
| MADDPG (upper bound) | 0.8340 |
| AllOffload | 0.5250 |
| NoOffload | 0.0000 |

**Ten of twelve rows — every method except the two we independently know are genuinely,
deterministically computed (AllOffload, NoOffload) — report the identical Fleet OTR value to four
decimal places, including MA-ROPE's own row.** Ten independently-run algorithms (a bandit, a genetic
algorithm, a Lyapunov controller, a greedy heuristic, four restricted-DQN ablations, a centralized
MADDPG upper bound, and MA-ROPE itself) do not produce a bit-identical stochastic-environment metric
by chance.

**It gets more specific, not less, on closer inspection:**

- `Jing2019 (Lyapunov)` and `Shao2025 (CoopEC)` are identical across **all five** reported columns
  (U_PRR, U_OTR, Fleet OTR, Energy, Latency: `0.8339, 0.7414, 0.8340, 0.5032, 275.6` — both rows,
  every digit).
- The separate "Safety-Task Delivery" table (`tab:safety_task`) reports `Wu2021`'s Safety PRR/OTR/gap
  as `0.9890, 0.7519, 23.7%` — **identical to MA-ROPE's own row in the same table**, to four decimal
  places and one decimal percentage point.
- `NoOffload`'s Energy (`0.5032`) in the main headline table matches `Jing2019`/`Shao2025`'s Energy
  exactly, despite NoOffload being a completely different (and, per `ENERGY_METRIC_DECISION.md`,
  dimensionally invalid) computation path.
- `AllOffload`'s Latency (`176.9`) matches `DQN — Jing constraints`' Latency exactly.

## What this means for Workstream 2

The original question — "should we implement MADDPG/CoopEC/Lyapunov/GA+DQN to match the table" — is
superseded. **There is nothing credible in the existing table to match.** Even a faithful, correct
implementation of any of these four algorithms would not "reproduce" these numbers, because the
numbers do not appear to derive from four independently-run algorithms in the first place. The
right framing is no longer "missing baselines" (Category G, as scoped in
`MANUSCRIPT_NUMBER_PROVENANCE_REPORT.md`) — it is that **most of this comparison table's contents
cannot be treated as evidence of anything** and need to be produced from scratch, independent of
whatever process generated the current values.

## What this does NOT establish

This is a pattern-level, evidence-based finding, not a claim about intent. I have not seen (and
have no access to) whatever process originally produced these rows — it's equally possible this
came from a template/placeholder table that was never replaced with real runs, a copy-paste error
propagated across drafts, or something else entirely. The evidence supports "these values are not
independently computed," not a claim about why.

## Recommendation

Do not treat implementing any of these four algorithms as a "reproduction" task — there is no
target to reproduce. If they're wanted in the paper, each would need to be implemented as a genuinely
new experiment, run against the current validated `V2XEnv`/`baseline_recreation` pipeline, with its
own campaign provenance (same rigor as `EXECUTION_CONTRACT_V3.md`), and reported as new results —
not compared against, or presented alongside, the current table's numbers for those methods.
Given the effort of implementing four additional algorithms faithfully (a bandit was tractable in an
afternoon; a Lyapunov drift-plus-penalty controller, a genetic-algorithm-tuned DQN, and a centralized
MADDPG critic are each substantially larger undertakings), **the realistic near-term options are:
(a) narrow the paper's comparison table to the methods that are genuinely implemented and validated
(MA-ROPE, AllOffload, NoOffload, UCB-RAT) and drop the other four rows entirely with a disclosed
note, or (b) treat implementing one or more of them as new, separately-scoped future work, not
part of closing out this reproduction.** This is a scope/resourcing decision for the professor and
Vivek, not one to make unilaterally here.
