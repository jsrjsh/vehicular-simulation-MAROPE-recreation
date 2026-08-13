import re

with open('MA_ROPE_TVT_LATEX/main.tex', 'r') as f:
    latex = f.read()

# Replace document class
latex = re.sub(r'\\documentclass\[.*?\]{.*?}', r'\\documentclass[journal,10pt,twocolumn]{IEEEtran}', latex)

# Add packages
packages = r'''
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{subcaption}
\usepackage{siunitx}
\usepackage{cite}
\usepackage{hyperref}
\usepackage{cleveref}
'''
latex = latex.replace(r'\begin{document}', packages + '\n' + r'\begin{document}')

# Remove hypertarget which pandoc uses for headings, let's keep it simple
# latex = re.sub(r'\\hypertarget{.*?}{%?\n\s*\\section{(.*?)}\\label{.*?}}', r'\\section{\1}', latex, flags=re.DOTALL)

with open('MA_ROPE_TVT_LATEX/main.tex', 'w') as f:
    f.write(latex)

