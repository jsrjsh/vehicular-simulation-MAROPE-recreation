# Repository Audit

## Classification

### A. Commit to Git
The following core assets are tracked to preserve the scientific integrity and reproducibility of the MA-ROPE paper:
- `src/maro_pe/`: The core environment (`env/`) and agent (`agents/`) logic.
- `scripts/`: Training, evaluation, and reproduction scripts.
- `tests/`: Automated unit and integration tests.
- `configs/`: YAML/JSON configuration files for reproducibility.
- `experiments/manifests/`: Formal metadata linking scripts to results.
- `results/reference/`: Distilled output CSVs containing final metrics reported in the paper.
- `manuscript/submission/`: The final, pre-submission `MA_ROPE_IEEE_Paper_v21.docx`.

**Reason**: These files form the minimal, self-contained subset of the project necessary to understand, run, and evaluate the published results without external context.

### B. Exclude via .gitignore
The `.gitignore` strictly prevents local clutter and generated artifacts from leaking into the repository:
- `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd` (Python bytecode)
- `*.log`, `*.out`, `*.err` (Execution logs)
- `checkpoints*/` (Large binary model weights)
- `*.tar.gz`, `*.zip` (Large archives)
- `*dump.txt` (Temporary debugging output)
- `results_diagnostics.json` (Local metadata)

**Reason**: These files change frequently across executions, consume excess bandwidth, or are not required for a downstream reviewer to validate the methodology. Large files are handled via Git LFS if strictly necessary.

### C. Archive outside repository
All internal notes from the debugging and development process were moved to an untracked `archive/` directory:
- `PHASE*.md`, `POLICY_*.md`, `QUEUE_*.md`, `V20_*.md`
- `REPRODUCIBILITY_REPORT.md`, `PROJECT_HEALTH_REPORT.md`, `REVIEWER_SUMMARY.md`
- Internal experiment notes (`EXP001.md`, `EXP002.md`)
- Legacy manuscript versions (e.g., `v20-2.docx`)
- `mode_research_artifact*.tar.gz`

**Reason**: This information tracks the internal engineering journey and forensics. Including them violates the anonymity and conciseness requirements for peer review and risks confusing external researchers.

### D. Requires manual review before committing
- Absolute path strings in `scripts/` (to be converted to relative).
- Identifying names in `README.md` or docstrings.
- All YAML configs to ensure no local laptop directories are hardcoded.

**Reason**: To maintain anonymity and environment independence.
