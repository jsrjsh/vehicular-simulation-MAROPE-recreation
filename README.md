# MA-ROPE: Multi-RAT Privacy-Preserving Federated DRL for V2X Task Offloading

## Overview
This repository contains the official implementation of the MA-ROPE algorithm, as submitted for IEEE peer review. MA-ROPE provides a fully decentralized, privacy-preserving, and communication-efficient task offloading framework for vehicular networks.

## Scientific Contribution
MA-ROPE uniquely combines:
1. Heterogeneous 4-RAT selection (LTE, ITS-G5, WiFi-6, 5G-NR).
2. SINR-proportional partial offload ratios.
3. Shared MEC queue contention modeling.
4. Privacy-preserving FedAvg deep reinforcement learning (Dueling Double DQN).

## Repository Structure
- `src/maro_pe/`: Core RL agents and vehicular environment simulation.
- `configs/`: Hyperparameters and experiment definitions.
- `scripts/`: Execution and reproduction scripts.
- `experiments/manifests/`: Formal experimental definitions.
- `results/reference/`: Pre-computed metrics for fast validation.
- `docs/reviewer_guide/`: Instructions for IEEE reviewers.

## Quick Start (Reviewer Mode)
To run a fast sanity check on the pipeline (verifies environment, action space, and model architecture without hours of training):
```bash
python scripts/reproduce_paper.py --config configs/experiments/paper_main.yaml --reviewer-mode
```

## Full Reproduction
To fully reproduce the N=32 benchmark results (Warning: takes ~6 hours on a CPU):
```bash
python scripts/reproduce_paper.py --config configs/experiments/paper_main.yaml
```

## Documentation
Please see [docs/reviewer_guide/REVIEWER_GUIDE.md](docs/reviewer_guide/REVIEWER_GUIDE.md) for detailed instructions on mapping generated outputs to paper figures and tables.

## Anonymous Review Note
This repository has been scrubbed of author metadata and identities to comply with double-blind review policies. Please do not submit PRs with identifying information if interacting during the review phase.
