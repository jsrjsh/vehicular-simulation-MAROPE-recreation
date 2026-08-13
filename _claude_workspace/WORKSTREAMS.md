# WORKSTREAMS.md — Track separation

Two independent tracks now run in this project. Keeping them physically and procedurally
separate so submission-line work and next-phase R&D never get mixed into the same decision or
the same file by accident.

## Track A — TVT Submission (current manuscript)
- **Directory**: `_claude_workspace/manuscript_revision/`
- **Status**: content complete (abstract, contributions, related work, system model, method,
  results, limitations, conclusion), compiled to PDF, real figures from validated data.
- **Depends on**: nothing outstanding from Track B. Does not need SUMO/ns-3 results to be
  submittable — the mobility/channel abstraction is already disclosed as a limitation.
- **Remaining work**: significance testing pass, true IEEEtran typesetting (see note below),
  your read-through, cover letter / author block.
- **Rule**: nothing from Track B gets pulled into this manuscript unless a specific new result
  from Track B is deliberately and explicitly added as a revision — never silently.

## Track B — SUMO+ns-3 next-phase R&D
- **Directory**: `vehicular-simulation/` (existing prototype, heuristic-only, no RL) +
  `_claude_workspace/EXECUTION_CONTRACT_V4_SUMO_NS3_VALIDATION.md` (the AG task, not yet run)
- **Status**: prior heuristic SUMO+ns-3 prototype assessed, Phase 1 contract written, not yet
  executed.
- **Depends on**: nothing from Track A.
- **Rule**: this track never touches `env/`, `agents/`, or any file under `results/CAMPAIGN_*`
  (already written into the contract). Its outputs land in their own
  `results/SUMO_NS3_VALIDATION_*/` directory.

## Note on the IEEEtran.cls file currently sitting in `manuscript_revision/latex/`
That copy is broken — the CTAN fetch was truncated (only ~1780 of the real file's lines came
through) and it's missing the title-block and keyword macros. Testing it produced a PDF with no
title, broken section numbers, and mangled keywords, so I've stopped using it. It's not deleted
(Projects_Claude files can't be removed without your say-so) but it should be ignored — the
draft PDF I've been sharing uses the plain-article fallback, not this file.

## How to tell which track a given file/action belongs to going forward
Every new file goes in one of the two directories above. Task list entries from here on will
be prefixed `[A]` or `[B]` so progress on one is never confused for progress on the other.
