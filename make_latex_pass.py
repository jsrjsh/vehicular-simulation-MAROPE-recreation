import os
os.makedirs('MA_ROPE_TVT_LATEX/sections', exist_ok=True)
os.makedirs('MA_ROPE_TVT_LATEX/figures', exist_ok=True)
os.makedirs('MA_ROPE_TVT_LATEX/tables', exist_ok=True)

main_tex = r"""\documentclass[journal,10pt,twocolumn]{IEEEtran}
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
\begin{document}
\title{MA-ROPE}
\author{Anonymous Authors}
\maketitle
\begin{abstract}This is the abstract.\end{abstract}
\section{Introduction}
Introduction \cite{shao2025coopec}.
\begin{equation}
a = b
\end{equation}
\begin{table}
\caption{Parameters}
\begin{tabular}{cc}
\toprule
A & B \\
\bottomrule
\end{tabular}
\end{table}
\begin{figure}
\includegraphics{figures/fig1.png}
\caption{Results figure}
\end{figure}
\begin{thebibliography}{1}
\bibitem{shao2025coopec} Dummy item.
\end{thebibliography}
\end{document}
"""
with open('MA_ROPE_TVT_LATEX/main.tex', 'w') as f:
    f.write(main_tex)

import base64
png = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
with open('MA_ROPE_TVT_LATEX/figures/fig1.png', 'wb') as f:
    f.write(base64.b64decode(png))
