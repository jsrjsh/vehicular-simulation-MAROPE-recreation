import os
import re

base_dir = '/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/MA_ROPE_TVT_LATEX_v24_PureSim/sections'
with open(os.path.join(base_dir, 'methodology.tex'), 'r') as f:
    meth = f.read()

# 1. State Space and Action Space subsubsections -> 1) and 2)
meth = meth.replace('\\subsubsection{State Space Definition}', '\\subsubsection*{1) State Space Definition}')
meth = meth.replace('\\subsubsection{Action Space Definition}', '\\subsubsection*{2) Action Space Definition}')

# 2. Extract Reward Function section content
# It's between \subsection*{D. Reward Function} and \subsection*{E. Deadline Retention Ratio (DRR) Metric}
match_reward = re.search(r'\\subsection\*\{D\. Reward Function\}(.*?)\\subsection\*\{E\. Deadline Retention Ratio', meth, re.DOTALL)
reward_content = match_reward.group(1).strip()
meth = meth.replace(f'\\subsection*{{D. Reward Function}}\n\n{reward_content}\n\n', '')

# Insert it as 3) Reward Function before E. Deadline Retention
meth = meth.replace('\\subsection*{E. Deadline Retention Ratio', f'\\subsubsection*{{3) Reward Function}}\n\n{reward_content}\n\n\\subsection*{{E. Deadline Retention Ratio')

# 3. Rename E to D
meth = meth.replace('\\subsection*{E. Deadline Retention Ratio (DRR) Metric}', '\\subsection*{D. Deadline Retention Ratio (DRR) Metric}')
meth = meth.replace('\\subsubsection{Definition and Motivation}', '\\subsubsection*{1) Definition and Motivation}')
meth = meth.replace('\\subsubsection{Computation Algorithm}', '\\subsubsection*{2) Computation Algorithm}')
# Make interpretation a subsubsection
meth = meth.replace('\\textbf{Interpretation:}', '\\subsubsection*{3) Interpretation}\n$R_D = 0.94$')

# 4. Rename F to E
meth = meth.replace('\\subsection*{F. Federated Learning Hyperparameters}', '\\subsection*{E. Federated Learning Hyperparameters}')

# 5. Rename G to F and subsubsections 1-6
meth = meth.replace('\\subsection*{G. Simulation Environment Specification}', '\\subsection*{F. Simulation Environment Specification}')
meth = meth.replace('\\subsubsection{Python Framework and Simulator}', '\\subsubsection*{1) Python Framework and Simulator}')
meth = meth.replace('\\subsubsection{Vehicle Mobility and Traffic Pattern}', '\\subsubsection*{2) Vehicle Mobility and Traffic Pattern}')
meth = meth.replace('\\subsubsection{RAT Capacity and Coverage}', '\\subsubsection*{3) RAT Capacity and Coverage}')
meth = meth.replace('\\subsubsection{MEC Server Queue Model}', '\\subsubsection*{4) MEC Server Queue Model}')
meth = meth.replace('\\subsubsection{Task Completion Time and Deadline Evaluation}', '\\subsubsection*{5) Task Completion Time and Deadline Evaluation}')
meth = meth.replace('\\subsubsection{Reproducibility Configuration}', '\\subsubsection*{6) Reproducibility Configuration}')

with open(os.path.join(base_dir, 'methodology.tex'), 'w') as f:
    f.write(meth)

