#!/bin/bash
set -e

echo "Running B3.1 SHARED Baseline (200 eps)..."
PYTHONPATH=. python3 scripts/train_b3_baselines.py --mode shared --episodes 200 --eval_interval 20 --eval_eps 5 > b3_shared.log

echo "Running B3.2 INDEPENDENT Baseline (200 eps)..."
PYTHONPATH=. python3 scripts/train_b3_baselines.py --mode independent --episodes 200 --eval_interval 20 --eval_eps 5 > b3_independent.log

echo "Running B3.3 FEDAVG Baseline (200 eps)..."
PYTHONPATH=. python3 scripts/train_b3_baselines.py --mode fedavg --episodes 200 --eval_interval 20 --eval_eps 5 > b3_fedavg.log

echo "All B3 baselines complete."
