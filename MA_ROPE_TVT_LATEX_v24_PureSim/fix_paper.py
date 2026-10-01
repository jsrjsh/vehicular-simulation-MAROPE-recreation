import os
import re

base_dir = '/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/MA_ROPE_TVT_LATEX_v24_PureSim/sections'

def remove_manual_letters(text):
    # Removes "A. ", "B. ", "IV-A. ", etc from \subsection{...}
    # But the user asked to specifically format them as: \subsection{A. Network Architecture}
    # Wait, the user said "organize as: \subsection{A. Network Architecture}"
    # BUT in standard IEEEtran, \subsection{} automatically adds "A.", "B.", etc.
    # If we manually add "A.", it will render as "A. A. Network Architecture".
    # I should check how it looks. I'll just rely on LaTeX's automatic numbering, 
    # but ensure the order of \subsection{} is exactly what the user wants.
    pass

# Read all files to memory
files = ['introduction.tex', 'related_work.tex', 'system_model.tex', 'methodology.tex', 'algorithm_design.tex', 'experiments.tex', 'results_part1.tex', 'results_part2.tex', 'conclusion.tex']
contents = {}
for file in files:
    with open(os.path.join(base_dir, file), 'r') as f:
        contents[file] = f.read()

# 1. Introduction bullets
intro = contents['introduction.tex']
intro = intro.replace('\\begin{itemize}', '')
intro = intro.replace('\\end{itemize}', '')
intro = intro.replace('\\item \\textbf{C1: Joint multi-RAT partial-offload optimization under shared queue contention.} We formulate', 'The first contribution is the joint optimization of multi-RAT selection and partial computation offloading under shared queue contention. We formulate')
intro = intro.replace('\\item \\textbf{C2: Federated, queue-aware deep RL with explicit multi-vehicle scalability.} We introduce', '\n\nThe second contribution is our development of a federated, queue-aware deep reinforcement learning framework with explicit multi-vehicle scalability. We introduce')
intro = intro.replace('\\item \\textbf{C3: Deadline-aware density evaluation paradigm.} We shift', '\n\nThe third contribution is a deadline-aware density evaluation paradigm. We shift')
intro = intro.replace('\\item \\textbf{C4: Rigorous dense-fleet scalability evaluation.} We demonstrate', '\n\nThe fourth contribution is a rigorous dense-fleet scalability evaluation. We demonstrate')
contents['introduction.tex'] = intro

# 2. System Model
# The order in the file is already Network Architecture, RAT Physical Layer Model, Task Model, End-to-End Latency Model, Energy and Utility.
# Let's ensure NO manual letters are inside \subsection{} to avoid double lettering.
sys = contents['system_model.tex']
sys = re.sub(r'\\subsection\{[A-Z]\.\s*', r'\\subsection{', sys)
contents['system_model.tex'] = sys

# 3. Methodology
meth = contents['methodology.tex']
# Let's structure Methodology to A-G exactly as requested.
# Remove any manual letters
meth = re.sub(r'\\subsection\{[A-Z]\.\s*', r'\\subsection{', meth)
meth = re.sub(r'\\subsubsection\{[A-Z]\d\.\s*', r'\\subsubsection{', meth)

# The user wants:
# A. System Model and Problem Formulation
# B. Task and Transmission Model (was subsubsection)
meth = meth.replace('\\subsection{Task and Transmission Model}', '\\subsection{Task and Transmission Model}') # it's already subsection from previous fix

# C. State, Action, and Reward Formulation
# Move State Space Definition and Action Space Definition under C as subsubsections? The user says: [current C content + "State Space Definition" + "Action Space Definition"]
# Wait, if they are just paragraphs, we can use \subsubsection.
meth = meth.replace('\\subsection{State Space Definition}', '\\subsubsection{State Space Definition}')
meth = meth.replace('\\subsection{Action Space Definition}', '\\subsubsection{Action Space Definition}')

# D. Reward Function
meth = meth.replace('\\subsection{Reward Function}', '\\subsection{Reward Function}')

# E. Deadline Retention Ratio (DRR) Metric
meth = meth.replace('\\subsection{Deadline Retention Ratio (DRR) Metric}', '\\subsection{Deadline Retention Ratio (DRR) Metric}')
meth = meth.replace('\\subsection{Definition and Motivation}', '\\subsubsection{Definition and Motivation}')
meth = meth.replace('\\subsection{Computation Algorithm}', '\\subsubsection{Computation Algorithm}')

# F. Federated Learning Hyperparameters
meth = meth.replace('\\subsection{Federated Learning Hyperparameters}', '\\subsection{Federated Learning Hyperparameters}')

# G. Simulation Environment Specification
meth = meth.replace('\\subsection{Simulation Environment Specification}', '\\subsection{Simulation Environment Specification}')
meth = meth.replace('\\subsection{Python Framework and Simulator}', '\\subsubsection{Python Framework and Simulator}')
meth = meth.replace('\\subsection{Vehicle Mobility and Traffic Pattern}', '\\subsubsection{Vehicle Mobility and Traffic Pattern}')
meth = meth.replace('\\subsection{Radio Access Technology (RAT) Capacity and Coverage}', '\\subsubsection{RAT Capacity and Coverage}')
meth = meth.replace('\\subsection{MEC Server Queue Model}', '\\subsubsection{MEC Server Queue Model}')
meth = meth.replace('\\subsection{Task Completion Time and Deadline Evaluation}', '\\subsubsection{Task Completion Time and Deadline Evaluation}')
meth = meth.replace('\\subsection{Reproducibility Configuration}', '\\subsubsection{Reproducibility Configuration}')
contents['methodology.tex'] = meth

# 4. Algorithm Design
alg = contents['algorithm_design.tex']
alg = re.sub(r'\\subsection\{[A-Z]\.\s*', r'\\subsection{', alg)
# Check for stray sections. The user says there is a duplicate B and a stray N.
# Wait, my grep for algorithm_design showed:
# \subsection{State and Action Space}
# \subsection{D3QN Architecture}
# \subsection{FedAvg Cooperative Learning}
# I will also add Baseline Methods here? The user says "D. Baseline Methods". 
# But "Baseline Methods" is currently in experiments.tex!
# Let me move it.
exp = contents['experiments.tex']
baseline_match = re.search(r'\\subsection\{Baseline Methods\}.*?(?=\\subsection|\Z)', exp, re.DOTALL)
if baseline_match:
    baseline_text = baseline_match.group(0)
    exp = exp.replace(baseline_text, '')
    alg += '\n' + baseline_text
contents['algorithm_design.tex'] = alg
contents['experiments.tex'] = exp

# 5. Experiments and Results
# Consolidate into experiments.tex
# Current structure of experiments.tex: Experimental Setup, Packet-Level Statistics.
# results_part1.tex: Algorithmic Comparison, Safety-Critical Task Delivery, Fleet-Density Scaling, Discussion
# results_part2.tex: Queue Contention, Computational Complexity
# The user wants:
# A. Experimental Setup
# B. Performance Metrics and Baseline Comparison
# C. Packet-Level Statistics Across V2X Interactions
# D. Algorithmic Comparison
# E. Safety-Critical Task Delivery
# F. Fleet-Density Scaling and RSU Queue Contention
# G. Discussion
# Where is "Performance Metrics"? Let me look at results_part2 or experiments.
# I will just write the files and then check manually.
for file in files:
    with open(os.path.join(base_dir, file), 'w') as f:
        f.write(contents[file])
