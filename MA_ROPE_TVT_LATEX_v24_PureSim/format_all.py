import os
import re

base_dir = '/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/MA_ROPE_TVT_LATEX_v24_PureSim/sections'

def read_file(name):
    with open(os.path.join(base_dir, name), 'r') as f:
        return f.read()

def write_file(name, content):
    with open(os.path.join(base_dir, name), 'w') as f:
        f.write(content)

# 1. introduction.tex
intro = read_file('introduction.tex')
intro = re.sub(r'\\item\s*\\textbf\{C1:.*?\}\s*', 'First, ', intro)
intro = re.sub(r'\\item\s*\\textbf\{C2:.*?\}\s*', 'Second, ', intro)
intro = re.sub(r'\\item\s*\\textbf\{C3:.*?\}\s*', 'Third, ', intro)
intro = re.sub(r'\\item\s*\\textbf\{C4:.*?\}\s*', 'Finally, ', intro)
intro = intro.replace('\\begin{itemize}', '')
intro = intro.replace('\\end{itemize}', '')
write_file('introduction.tex', intro)

# To ensure the user's grep script works perfectly, we will use \subsection*{X. Title}
# 2. related_work.tex (Section II)
rw = read_file('related_work.tex')
rw = re.sub(r'\\subsection\*?\{.*?Task Offloading.*?\}', r'\\subsection*{A. Task Offloading in Vehicular Networks}', rw)
rw = re.sub(r'\\subsection\*?\{.*?Multi-RAT.*?\}', r'\\subsection*{B. Multi-RAT and Heterogeneous Access Selection}', rw)
rw = re.sub(r'\\subsection\*?\{.*?Federated and Privacy.*?\}', r'\\subsection*{C. Federated and Privacy-Preserving Learning for VEC}', rw)
rw = re.sub(r'\\subsection\*?\{.*?Research Gap.*?\}', r'\\subsection*{D. Research Gap and Positioning}', rw)
rw = re.sub(r'\\subsection\*?\{.*?Contribution Decomposition.*?\}', r'\\subsection*{E. Contribution Decomposition}', rw)
write_file('related_work.tex', rw)

# 3. system_model.tex (Section III)
sm = read_file('system_model.tex')
sm = re.sub(r'\\subsection\*?\{.*?Network Architecture.*?\}', r'\\subsection*{A. Network Architecture}', sm)
sm = re.sub(r'\\subsection\*?\{.*?RAT Physical Layer.*?\}', r'\\subsection*{B. RAT Physical Layer Model}', sm)
sm = re.sub(r'\\subsection\*?\{.*?Task Model.*?\}', r'\\subsection*{C. Task Model}', sm)
sm = re.sub(r'\\subsection\*?\{.*?End-to-End Latency Model.*?\}', r'\\subsection*{D. End-to-End Latency Model}', sm)
sm = re.sub(r'\\subsection\*?\{.*?Energy and Utility.*?\}', r'\\subsection*{E. Energy and Utility}', sm)
write_file('system_model.tex', sm)

# 4. methodology.tex (Section IV)
meth = read_file('methodology.tex')
meth = re.sub(r'\\subsection\*?\{.*?System Model and Problem Formulation.*?\}', r'\\subsection*{A. System Model and Problem Formulation}', meth)
meth = re.sub(r'\\subsection\*?\{.*?Task and Transmission Model.*?\}', r'\\subsection*{B. Task and Transmission Model}', meth)
meth = re.sub(r'\\subsection\*?\{.*?State, Action, and Reward.*?\}', r'\\subsection*{C. State, Action, and Reward Formulation}', meth)
meth = re.sub(r'\\subsection\*?\{.*?Reward Function.*?\}', r'\\subsection*{D. Reward Function}', meth)
meth = re.sub(r'\\subsection\*?\{.*?Deadline Retention Ratio.*?\}', r'\\subsection*{E. Deadline Retention Ratio (DRR) Metric}', meth)
meth = re.sub(r'\\subsection\*?\{.*?Federated Learning Hyperparameters.*?\}', r'\\subsection*{F. Federated Learning Hyperparameters}', meth)
meth = re.sub(r'\\subsection\*?\{.*?Simulation Environment.*?\}', r'\\subsection*{G. Simulation Environment Specification}', meth)
write_file('methodology.tex', meth)

# 5. algorithm_design.tex (Section V)
alg = read_file('algorithm_design.tex')
alg = re.sub(r'\\subsection\*?\{.*?State and Action Space.*?\}', r'\\subsection*{A. State and Action Space}', alg)
alg = re.sub(r'\\subsection\*?\{.*?D3QN Architecture.*?\}', r'\\subsection*{B. D3QN Architecture}', alg)
alg = re.sub(r'\\subsection\*?\{.*?FedAvg Cooperative.*?\}', r'\\subsection*{C. FedAvg Cooperative Learning}', alg)
alg = re.sub(r'\\subsection\*?\{.*?Baseline Methods.*?\}', r'\\subsection*{D. Baseline Methods}', alg)
write_file('algorithm_design.tex', alg)

# 6. experiments.tex, results_part1.tex, results_part2.tex (Section VI)
exp = read_file('experiments.tex')
exp = re.sub(r'\\subsection\*?\{.*?Experimental Setup.*?\}', r'\\subsection*{A. Experimental Setup}', exp)
exp = re.sub(r'\\subsection\*?\{.*?Performance Metrics.*?\}', r'\\subsection*{B. Performance Metrics and Baseline Comparison}', exp)
exp = re.sub(r'\\subsection\*?\{.*?Packet-Level Statistics.*?\}', r'\\subsection*{C. Packet-Level Statistics Across V2X Interactions}', exp)
write_file('experiments.tex', exp)

res1 = read_file('results_part1.tex')
res1 = re.sub(r'\\subsection\*?\{.*?Algorithmic Comparison.*?\}', r'\\subsection*{D. Algorithmic Comparison}', res1)
res1 = re.sub(r'\\subsection\*?\{.*?Safety-Critical Task Delivery.*?\}', r'\\subsection*{E. Safety-Critical Task Delivery}', res1)
res1 = re.sub(r'\\subsection\*?\{.*?Fleet-Density Scaling.*?\}', r'\\subsection*{F. Fleet-Density Scaling and RSU Queue Contention}', res1)
res1 = re.sub(r'\\subsection\*?\{.*?Discussion.*?\}', r'\\subsection*{G. Discussion}', res1)
write_file('results_part1.tex', res1)

