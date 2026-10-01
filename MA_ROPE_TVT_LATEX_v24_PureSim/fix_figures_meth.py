import os
import re

file_path = '/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/MA_ROPE_TVT_LATEX_v24_PureSim/sections/methodology.tex'
with open(file_path, 'r') as f:
    content = f.read()

# Find the figure block containing image4.png
match = re.search(r'\\begin\{figure\}.*?image4\.png.*?\\end\{figure\}\n*', content, re.DOTALL)
if match:
    fig_block = match.group(0)
    content = content[:match.start()] + content[match.end():]

# New figure 2a definition
new_fig = r"""\renewcommand{\thefigure}{2a}
\begin{figure}[htbp]
\centering
\includegraphics[width=0.45\textwidth]{figures/image4.png}
\caption{Overall System Model showing task offloading flow, MDP state and action space, and end-to-end latency components.}
\label{fig:2a}
\end{figure}
\addtocounter{figure}{-1}
\renewcommand{\thefigure}{\arabic{figure}}

"""

# Insert at the very beginning after \section{Methodology}
insert_pos = content.find(r'\section{Methodology}') + len(r'\section{Methodology}') + 1
content = content[:insert_pos] + new_fig + content[insert_pos:]

# Replace references to fig:mdp_formulation with fig:2a
content = content.replace('fig:mdp_formulation', 'fig:2a')

with open(file_path, 'w') as f:
    f.write(content)

