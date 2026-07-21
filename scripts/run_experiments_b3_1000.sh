#!/bin/bash

# MA-ROPE+ Phase B3 Five-Seed Final Experiments (Long Horizon)
# This script executes the shared, independent, and fedavg baselines across 5 seeds for 1000 episodes.

SEEDS=(42 43 44 45 46)
MODES=("shared" "independent" "fedavg")
EPISODES=1000
EVAL_INTERVAL=20

export PYTHONPATH=.

for mode in "${MODES[@]}"; do
    for seed in "${SEEDS[@]}"; do
        echo "=================================================="
        echo "Running mode: $mode | Seed: $seed | Episodes: $EPISODES"
        echo "=================================================="
        python3 scripts/train_b3_baselines.py --mode $mode --episodes $EPISODES --eval_interval $EVAL_INTERVAL --seed $seed > logs_${mode}_seed_${seed}.txt 2>&1
    done
done

echo "All 15 experiments (1000 episodes) completed successfully."
