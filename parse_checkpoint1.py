import os
import re

with open('docx_content.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

abstract_lines = []
intro_lines = []

state = None

for line in lines:
    clean = line.strip()
    if clean.lower().startswith('# abstract') or clean.lower() == 'abstract':
        state = 'abstract'
        continue
    if clean.lower().startswith('# 1. introduction') or clean.lower() == '# i. introduction':
        state = 'intro'
        continue
    if clean.lower().startswith('# 2. related work') or clean.lower() == '# ii. related work':
        break
        
    if state == 'abstract':
        if clean: abstract_lines.append(clean)
    elif state == 'intro':
        if clean: intro_lines.append(clean)

def md_to_latex(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    text = re.sub(r'\[(\d+)\]', r'\\cite{\1}', text)
    return text

abstract_tex = "\n\n".join([md_to_latex(p) for p in abstract_lines])
intro_tex = "\n\n".join([md_to_latex(p) for p in intro_lines])

os.makedirs('MA_ROPE_TVT_LATEX/sections', exist_ok=True)

with open('MA_ROPE_TVT_LATEX/sections/abstract.tex', 'w', encoding='utf-8') as f:
    f.write("\\begin{abstract}\n" + abstract_tex + "\n\\end{abstract}\n")

with open('MA_ROPE_TVT_LATEX/sections/introduction.tex', 'w', encoding='utf-8') as f:
    f.write("\\section{Introduction}\n" + intro_tex + "\n")

main_tex = r"""\documentclass[journal,10pt,twocolumn]{IEEEtran}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{siunitx}
\usepackage{cite}
\usepackage{hyperref}
\usepackage{cleveref}

\begin{document}

\title{MA-ROPE: Multi-RAT Privacy-Preserving Federated Deep Reinforcement Learning for V2X Task Offloading}
\author{Original Authors}

\maketitle

\input{sections/abstract}
\input{sections/introduction}

\end{document}
"""

with open('MA_ROPE_TVT_LATEX/main.tex', 'w', encoding='utf-8') as f:
    f.write(main_tex)

