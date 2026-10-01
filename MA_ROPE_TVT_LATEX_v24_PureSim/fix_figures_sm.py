import os

file_path = '/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/MA_ROPE_TVT_LATEX_v24_PureSim/sections/system_model.tex'
with open(file_path, 'r') as f:
    content = f.read()

new_fig = r"""\renewcommand{\thefigure}{2b}
\begin{figure}[htbp]
\centering
\includegraphics[width=0.45\textwidth]{figures/image3.png}
\caption{Network Topology with 4-RAT heterogeneous access and FedAvg coordination.}
\label{fig:2b}
\end{figure}
\addtocounter{figure}{-1}
\renewcommand{\thefigure}{\arabic{figure}}"""

# Find the figure block containing image3.png
import re
match = re.search(r'\\begin\{figure\}.*?image3\.png.*?\\end\{figure\}', content, re.DOTALL)
if match:
    content = content[:match.start()] + new_fig + content[match.end():]

# Update references to fig:architecture
content = content.replace('fig:architecture', 'fig:2b')

with open(file_path, 'w') as f:
    f.write(content)

