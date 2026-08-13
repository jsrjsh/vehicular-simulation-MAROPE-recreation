with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Replace \textbf{\textit{...}} with \subsection{...}
text = text.replace(r'\textbf{\textit{A. TASK OFFLOADING IN VEHICULAR NETWORKS}}', r'\subsection{Task Offloading in Vehicular Networks}')
text = text.replace(r'\textbf{\textit{B. RESEARCH GAP}}', r'\subsection{Research Gap}')
text = text.replace(r'\subsection{CONTRIBUTION DECOMPOSITION}', r'\subsection{Contribution Decomposition}')

# Format Table I properly
table_content = r"""
\begin{table}[htbp]
\caption{Literature Comparison --- Feature Coverage}
\label{tab:literature}
\centering
\begin{tabular}{|l|c|c|c|c|c|c|}
\hline
\textbf{Paper} & \textbf{Multi-RAT} & \textbf{Partial $\rho$} & \textbf{Queue Cont.} & \textbf{FL Privacy} & \textbf{Jakes} & \textbf{Yacheur Ch.} \\
\hline
Guo 2026 [8] & $\times$ & Partial & Per-node & $\times$ & $\times$ & $\times$ \\
Yacheur 2023 [9] & \checkmark ITS+LTE & $\times$ & $\times$ & $\times$ & \checkmark & \checkmark \\
Shao 2025 [3] & $\times$ & $\times$ & $\times$ & \checkmark FedAvg & $\times$ & $\times$ \\
Wu 2021 [4] & $\times$ & $\times$ & $\times$ & $\times$ & $\times$ & $\times$ \\
\textbf{MA-ROPE (ours)} & \textbf{\checkmark 4 RATs} & \textbf{\checkmark $\rho\in\{0..1\}$} & \textbf{\checkmark shared RSU} & \textbf{\checkmark FedAvg} & \textbf{\checkmark Jakes} & \textbf{\checkmark adopted} \\
\hline
\end{tabular}
\end{table}
"""
import re
text = re.sub(r'\\textbf{TABLE I.*?-----------', table_content, text, flags=re.DOTALL)

# Format Figures 1 and 2
text = text.replace('Fig. 1. Contribution waterfall (URLLC, N=8 reference). AllOffload baseline (U=0.8166) to MA-ROPE full (U=0.8443): each component contributes independently.',
r"""\begin{figure}[htbp]
\centering
\includegraphics[width=0.45\textwidth]{example-image-a}
\caption{Contribution waterfall (URLLC, N=8 reference). AllOffload baseline (U=0.8166) to MA-ROPE full (U=0.8443): each component contributes independently.}
\label{fig:waterfall}
\end{figure}""")

text = text.replace('Fig. 2. Literature gap matrix. MA-ROPE (bottom row, blue highlight) is the only framework with all six properties: supported, partial, or not supported.',
r"""\begin{figure}[htbp]
\centering
\includegraphics[width=0.45\textwidth]{example-image-b}
\caption{Literature gap matrix. MA-ROPE (bottom row, blue highlight) is the only framework with all six properties: supported, partial, or not supported.}
\label{fig:gap_matrix}
\end{figure}""")

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

