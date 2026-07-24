# Reviewer Guide

Welcome, Reviewer. This guide will help you install the repository and reproduce the results presented in the MA-ROPE paper.

## 1. Install Dependencies
Ensure you have Python 3.9+ installed.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Run Smoke Tests
Verify the environment and architecture are working locally.
```bash
pytest -q
```

## 3. Run Reviewer Mode (Fast Validation)
To validate the workflow end-to-end without spending hours training models, run the reviewer mode. This executes the entire pipeline for just 2 episodes on a single seed.
```bash
python scripts/reproduce_paper.py --config configs/experiments/paper_main.yaml --reviewer-mode
```

## 4. Reproduce Main Result
To execute the full N=32 comparison across 5 seeds:
```bash
python scripts/reproduce_paper.py --config configs/experiments/paper_main.yaml
```
*(Expected Runtime: ~6 hours on a modern CPU).*

## 5. Locating Paper Tables and Figures
After running the reproduction, results are placed in `results/`.
- **Table IIIa** corresponds to the aggregated metrics from `results_fedavg.csv` vs `results_independent.csv`.
- **Fig 10 and Fig 12** plot data extracted from these CSVs over the fleet size configurations.

## 6. Inspecting Reference Outputs
If you do not wish to train the models yourself, you can examine our pre-compiled outputs in `results/reference/`. These exactly match the statistics submitted in the paper.

## 7. Expected Deviations
RL training can be sensitive to hardware float precision differences (e.g., between Intel and Apple Silicon CPUs). We expect a tolerance of `+/- 1.5%` in reported metrics like On-Time Rate (OTR).

## 8. Reporting Issues
If you encounter any discrepancies, please securely provide feedback through the official conference peer-review system.
