# MANUSCRIPT_REVISION_DRAFT_v1 — Master + Roadmap

Written as head of this revision, per Vivek's direction to drop the recreation/reproduction framing
entirely and write forward from validated results and current literature. This directory
(`manuscript_revision/`) is a clean-slate working draft — it does not reference "canonical vs.
manuscript," "Path A/B," or any prior-version discrepancy. Those documents remain in the workspace
as the audit trail that got us here, but none of that framing belongs in the paper itself.

Files in this draft so far:
- `01_ABSTRACT_AND_CONTRIBUTIONS.md` — done
- `02_RESULTS_SECTION.md` — done
- `03_RELATED_WORK_AND_POSITIONING.md` — done

## Why the old "discrepancy" framing disappears entirely in this draft

Every prior report in this workspace (forensic report, claim-by-claim impact memo, etc.) existed
to answer one question: can the *previous* manuscript's numbers be defended. That question is now
irrelevant to this draft — we are not defending or reconciling old numbers, we are reporting this
campaign's validated results as the paper's own findings. The U_PRR/U_OTR "bounded-unresolved"
question, for instance, was only a problem *because* it was being compared against a number in an
old PDF; reported fresh, 0.9583/0.5252 are just MA-ROPE's real, validated numbers, no caveat
needed. This is the concrete benefit of dropping the baggage: several pages of "why does this
differ" analysis that would have been needed simply don't apply to a forward-written paper.

## What's done vs. what's left

**Done, real content, ready for review:**
1. Abstract + 6 numbered contributions
2. Full Results section (headline table, reliability decomposition, density scaling, training-
   duration robustness, explicit baseline-scope disclosure)
3. Related Work positioned against 6 real, cited 2023-2026 sources plus 4 patents, ending in an
   explicit gap statement

**Not yet drafted — real writing work still ahead, listed honestly rather than glossed over:**

4. **Introduction** — needs the motivation/problem-statement expansion (why multi-RAT + privacy +
   federation matters, framed by the Related Work gap). This is mostly a reordering/expansion of
   material already in 01 and 03, not new research — a half-day writing task.
5. **System Model** — the V2X environment, 4 RATs, 11-action space, dual utility functions
   (U_PRR/U_OTR). This describes the actual implemented simulator (`env/environment.py`,
   `env/config.py`) — factual/technical writing from the existing codebase, not something that
   needs new decisions. Straightforward to draft next.
6. **Method** — the MA-ROPE algorithm itself: D3QN+PER per-agent architecture, FedAvg aggregation
   schedule, Gaussian LDP mechanism and its privacy-budget parameterization. Also a description
   task from existing, working code — no new design work required.
7. **Limitations** — three items to state plainly: Energy is omitted (dimensionally invalid
   formula in the legacy compute mode, not fixable in scope — full reasoning in
   `ENERGY_METRIC_DECISION.md`); only two non-learned baselines are compared, both disclosed
   reconstructions, because the originally-intended comparators had no recoverable implementation;
   the literature scan is a targeted search, not a systematic review. All three are already fully
   reasoned in existing workspace documents — this section is compilation, not new analysis.
8. **Conclusion** — short, follows directly from Results + Contributions once both are final.
9. **Figures** — Fleet OTR vs. density (line plot, 4 series), reliability decomposition bar chart
   (conditional vs. fleet-wide, grouped by method), training-duration stability plot (3 seeds × 3
   checkpoints). All plottable directly from existing CSVs
   (`CORRECTED_BASELINE_RESULTS.csv`, `TRAINING_DURATION_RESULTS.csv`) — no new data needed.
10. **Bibliography additions** — the 6 papers and 4 patents cited in `03_RELATED_WORK_AND_POSITIONING.md`
    need full BibTeX entries added to `references.bib`. Straightforward, mechanical.

## Recommended next step

Sections 5-6 (System Model, Method) are the largest remaining piece and are pure technical
description of code that already exists and works — no scientific decision-making left, just
careful writing. That's the natural next task to pick up. Figures (item 9) can be generated in
parallel any time, since the data's already validated and sitting in CSV.

Nothing in items 4-10 requires new experiments, new decisions, or further forensic work — it's
writing against material that's already settled. Say the word and I'll keep going through System
Model and Method next.
