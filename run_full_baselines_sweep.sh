#!/bin/bash
cd vehicular-simulation/ns-3/marope_ns3_script
source ../../../.venv/bin/activate
for policy in ma-rope alloffload nooffload ucb_bandit coopec_greedy; do
  for N in 8 16 32; do
    for seed in 0 1 2 3 4; do
      echo "=== Running policy=$policy, N=$N, seed=$seed ==="
      python3 -u ../../../scripts/ns3_eval_baselines.py --policy_type $policy --n_vehicles $N --seed $seed
    done
  done
done
