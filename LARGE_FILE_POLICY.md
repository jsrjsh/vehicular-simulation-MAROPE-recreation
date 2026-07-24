# Large File Policy

## Background
The MA-ROPE project generates significant data during multi-agent reinforcement learning (MARL) training. These include:
- `checkpoints*/`: Saved neural network weights.
- `logs*/`: Detailed episodic stepping information.
- `results_*.csv`: The raw transaction logs for tens of thousands of tasks.

## Policy Rules
To keep this repository lightweight, clone-friendly, and easy to distribute for peer review:

1. **Never commit checkpoints to the main branch.** Training must be reproducible from scratch. Checkpoints should only be stored externally (e.g., via Zenodo, Hugging Face, or institutional storage).
2. **Never commit uncompressed raw logs.**
3. **Reference Data Only.** Only the final aggregated summary CSVs (`results_fedavg.csv`, `results_independent.csv`) required to reproduce the paper's plots and tables are tracked in the `results/reference/` directory.

## Git LFS
Currently, **Git LFS is disabled** to ensure maximum compatibility for anonymous reviewers without relying on third-party LFS quotas. The required reference results are small enough (<< 1 MB each) to be natively tracked in Git.

If future iterations require sharing pre-trained models, Git LFS must be explicitly enabled and `.gitattributes` must be updated to track `*.pt` and `*.pth` files.
