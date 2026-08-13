import re
import os

with open('MA_ROPE_TVT_LATEX/main.tex', 'r', encoding='utf-8') as f:
    tex = f.read()

# Fix longtables to tabular
# We need to find \begin{longtable}[]{@{}ll@{}} and replace it with \begin{table*} \begin{tabular}{@{}ll@{}}
tex = re.sub(r'\\begin\{longtable\}\[\]\{(@\{.*?\}.*?)\}', r'\\begin{table*}[htbp]\n\\centering\n\\begin{tabular}{\1}', tex)

tex = tex.replace(r'\end{longtable}', r'\end{tabular}' + '\n' + r'\end{table*}')
tex = re.sub(r'\\endhead', '', tex)
tex = re.sub(r'\\endfirsthead', '', tex)
tex = re.sub(r'\\endlastfoot', '', tex)
tex = re.sub(r'\\endfoot', '', tex)
tex = re.sub(r'\\toprule\(\)', r'\\toprule', tex)
tex = re.sub(r'\\bottomrule\(\)', r'\\bottomrule', tex)
tex = re.sub(r'\\midrule\(\)', r'\\midrule', tex)

# Replace unicode greek with latex math
greek_map = {
    'α': r'$\alpha$', 'β': r'$\beta$', 'γ': r'$\gamma$', 'δ': r'$\delta$', 
    'ε': r'$\varepsilon$', 'ζ': r'$\zeta$', 'η': r'$\eta$', 'θ': r'$\theta$', 
    'ι': r'$\iota$', 'κ': r'$\kappa$', 'λ': r'$\lambda$', 'μ': r'$\mu$', 
    'ν': r'$\nu$', 'ξ': r'$\xi$', 'ο': r'$o$', 'π': r'$\pi$', 
    'ρ': r'$\rho$', 'σ': r'$\sigma$', 'τ': r'$\tau$', 'υ': r'$\upsilon$', 
    'φ': r'$\phi$', 'χ': r'$\chi$', 'ψ': r'$\psi$', 'ω': r'$\omega$',
    'Δ': r'$\Delta$', 'Σ': r'$\Sigma$', '∈': r'$\in$', '≥': r'$\geq$', '≤': r'$\leq$',
    '·': r'$\cdot$', '✓': r'\checkmark', '✗': r'$\times$'
}
for k, v in greek_map.items():
    tex = tex.replace(k, v)

# Strip preamble and inject IEEEtran
parts = tex.split(r'\begin{document}', 1)

preamble = r"""\documentclass[journal,10pt,twocolumn]{IEEEtran}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{siunitx}
\usepackage{cite}
\usepackage{hyperref}
\usepackage{cleveref}
\usepackage{algorithm}
\usepackage{algorithmicx}
"""

tex = preamble + "\n\\begin{document}\n" + parts[1]

# Fix figure paths
tex = tex.replace('MA_ROPE_TVT_LATEX/figures/media/', 'figures/')
if os.path.exists('MA_ROPE_TVT_LATEX/figures/media'):
    os.system('mv MA_ROPE_TVT_LATEX/figures/media/* MA_ROPE_TVT_LATEX/figures/')

with open('MA_ROPE_TVT_LATEX/main.tex', 'w', encoding='utf-8') as f:
    f.write(tex)

