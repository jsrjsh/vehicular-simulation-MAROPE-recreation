import os
import re

base_dir = '/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/MA_ROPE_TVT_LATEX_v24_PureSim/sections'

# 1. experiments.tex
with open(os.path.join(base_dir, 'experiments.tex'), 'r') as f:
    exp = f.read()

# Add "B. Performance Metrics and Baseline Comparison" before "Packet-Level Statistics"
if 'Performance Metrics and Baseline Comparison' not in exp:
    exp = exp.replace('\\subsection{Packet-Level Statistics Across V2X Interactions}', '\\subsection{Performance Metrics and Baseline Comparison}\n\nThe performance metrics focus on deadline compliance and reliability compared against standard baselines.\n\n\\subsection{Packet-Level Statistics Across V2X Interactions}')

with open(os.path.join(base_dir, 'experiments.tex'), 'w') as f:
    f.write(exp)


# 2. results_part1.tex
with open(os.path.join(base_dir, 'results_part1.tex'), 'r') as f:
    res1 = f.read()
# It has: Algorithmic Comparison, Safety-Critical Task Delivery, Fleet-Density Scaling and RSU Queue Contention, Discussion
# Ensure no manual lettering
res1 = re.sub(r'\\subsection\{[A-Z]\.\s*', r'\\subsection{', res1)
with open(os.path.join(base_dir, 'results_part1.tex'), 'w') as f:
    f.write(res1)


# 3. results_part2.tex
with open(os.path.join(base_dir, 'results_part2.tex'), 'r') as f:
    res2 = f.read()
# Queue Contention and Key Findings -> convert to \subsubsection so it doesn't break the A-G lettering
res2 = res2.replace('\\subsection{Queue Contention and Key Findings}', '\\subsubsection{Queue Contention and Key Findings}')
res2 = res2.replace('\\subsection{Computational Complexity and Runtime Overhead}', '\\subsubsection{Computational Complexity and Runtime Overhead}')
with open(os.path.join(base_dir, 'results_part2.tex'), 'w') as f:
    f.write(res2)

