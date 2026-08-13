# GO_NO_GO_DECISION.md

Final PI-level decision after independently validating both `EXECUTION_CONTRACT_V3.md` deliverables
and producing `CORRECTED_RESULT_TABLES.md` and `CLAIM_BY_CLAIM_MANUSCRIPT_IMPACT.md`. This updates
`PUBLICATION_DECISION.md`'s earlier conditional verdict (written before real corrected data existed)
with a decision grounded in validated numbers.

## Validation status: PASS

Both `CAMPAIGN_CORRECTED_20260803` (60/60 combinations) and `CAMPAIGN_TRAINING_DURATION_20260803`
(3/3 checkpoints) passed independent verification — code hash recomputation, checkpoint hash and
all-agent-entry recomputation from actual file bytes, structural invariants, a cross-campaign
determinism check (14/15 `ma-rope` checkpoints bit-identical to Path A across two fully separate
executions), and an independent from-scratch re-execution of the new UCB-RAT baseline matching to 15
significant digits. One metadata bug was found and fixed (stale `wu2021_status` text — not a data
error). Full detail in `CLAUDE_FINDINGS.md`. **Nothing here was accepted on the executor's word
alone.**

## Three separate GO/NO-GO questions, answered separately

**1. Can manuscript revision work begin now, using this data?**

**GO.** The data is validated, the claim-by-claim impact is mapped (`CLAIM_BY_CLAIM_MANUSCRIPT_IMPACT.md`),
and roughly half the headline table has real, defensible replacement numbers ready to drop in
(U_PRR, U_OTR, Fleet OTR rows; Latency for MA-ROPE/NoOffload as-is). The Fleet OTR density-scaling
narrative and a fuller, more honest queue-loss/reliability story are both *stronger* than what the
manuscript currently claims and are ready to write.

**2. Is the manuscript ready to send to the professor as a complete, submission-track draft?**

**NO-GO — but now purely because the manuscript hasn't been drafted yet, not because of open data or
decision blockers.** All three original post-validation blockers are resolved:

- **Energy: RESOLVED — remove.** Traced to its exact source (`ENERGY_METRIC_DECISION.md`): the
  `baseline_recreation` energy formula is not a units bug, it's a dimensionally invalid equation
  (the code's own comment calls it a "literal rendering formula"), unfixable within scope without a
  simulator redesign. Verdict: do not report Energy for this reproduction. Final, not pending.
- **Baseline gap: RESOLVED by decision, not fully closed.** Investigating the four other named
  baselines surfaced a bigger problem than a missing-implementation gap — the manuscript's own
  headline table shows 10 of 12 rows sharing an identical Fleet OTR value, including MA-ROPE's own
  row (`BASELINE_TABLE_INTEGRITY_FINDING.md`) — there was no credible target to reproduce against.
  Decision taken: implemented `coopec_greedy` ("CoopEC-RAT") as a genuinely new, non-trivial
  baseline — now the most competitive alternative found (Fleet OTR 0.801 at N=32, lowest
  conditional failure rate of any offloading policy). MADDPG and GA+DQN-Yun2022 are dropped from the
  comparison entirely. Lyapunov-Jing2019 is queued as future work, not done this round — this is
  the one piece of this blocker still open.
- **Training-duration diagnostic: RESOLVED, now three seeds.** Expanded to seeds 1 and 2 at N=32;
  independently validated all 9 checkpoints (hash recomputation, all-agent entry count, genuine
  pairwise divergence). The within-seed training-duration effect (100→500 episodes) is the same size
  as, or smaller than, ordinary cross-seed noise, and its direction is inconsistent across seeds —
  not the signature of a real training-duration effect. This closes the last of the original three
  blockers: "Path B, not Path C" is now supported by three independent seeds, not one.

**All three original post-validation blockers are now resolved.** No open items remain before
manuscript drafting can begin in earnest.

**One more thing found and fixed along the way, not swept under the rug**: validating the seed
expansion turned up a real concurrency bug — AG ran seed 1 and seed 2 in parallel, and a
read-modify-write race in the diagnostic's manifest-saving code silently dropped all three of seed
1's entries from `manifest.json` (though not from the CSV, which is append-only and unaffected).
Caught by validation, not assumed away: reconstructed the missing entries from the independently
verified CSV and checkpoint files, and fixed the underlying race (`_merge_and_save_manifest()`,
reload-and-merge before every write) so future concurrent runs can't silently lose data the same
way. Smoke-tested the fix with a simulated concurrent-write race before trusting it. Full detail in
`CLAUDE_FINDINGS.md`.

**3. Is this worth showing the professor as a status update, separate from a submission-track draft?**

**Optional GO, framed as progress, not completion.** The validated campaign, the new non-trivial
baseline, and the resolved queue-loss mechanism are genuine, well-evidenced improvements over where
this stood a few sessions ago. `PROFESSOR_BRIEFING.md` (written before this validation) already
captures the right tone for this; it does not need a rewrite to reflect this round's results unless
Vivek wants the specific new numbers included.

## What happens next, in order

1. ~~Fix the Energy unit-conversion defect~~ — resolved: remove Energy from reporting, not fixable
   in scope.
2. ~~Make the explicit call on the four newly-identified missing baselines~~ — resolved:
   CoopEC-RAT implemented and validated; MADDPG/GA+DQN dropped; Lyapunov-Jing2019 queued as future
   work (not blocking).
3. ~~Expand the training-duration diagnostic to more seeds~~ — resolved: 3 seeds now, consistent
   result, a real concurrency bug found and fixed along the way.
4. **Next and only remaining step**: begin drafting the actual manuscript revisions using
   `CLAIM_BY_CLAIM_MANUSCRIPT_IMPACT.md` as the section-by-section input, and generate corrected
   figures. This is Phase 8/9 of the overall mission and has not started.

**Do not send any manuscript version to the professor as "ready" before step 4 is complete.** The
data gate that was blocking manuscript work is now open; the manuscript itself is not yet written.
