#!/bin/bash
cd vehicular-simulation/ns-3/marope_ns3_script
source ../../../.venv/bin/activate
for n in 8 16 32; do
  for seed in 0 1 2; do
    echo "Running N=${n}, Seed=${seed}"
    python3 -u ../../../scripts/ns3_eval_ma_rope.py --n_vehicles $n --seed $seed
  done
done
