import re
import os

with open('MA_ROPE_TVT_LATEX/main.tex', 'r', encoding='utf-8') as f:
    tex = f.read()

# Fix documentclass
tex = re.sub(r'\\documentclass\[.*?\]\{.*?\}', r'\\documentclass[journal,10pt,twocolumn]{IEEEtran}', tex, count=1)

# Add packages
packages = r'''
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{siunitx}
\usepackage{cite}
\usepackage{hyperref}
\usepackage{cleveref}
\usepackage{unicode-math}
\setmathfont{Latin Modern Math}
'''
tex = tex.replace(r'\begin{document}', packages + '\n' + r'\begin{document}')

# Remove hypertarget labels that cause issues
tex = re.sub(r'\\hypertarget{.*?}{%?\n\s*\\section{(.*?)}\\label{.*?}}', r'\\section{\1}', tex, flags=re.DOTALL)
tex = re.sub(r'\\hypertarget{.*?}{%?\n\s*\\subsection{(.*?)}\\label{.*?}}', r'\\subsection{\1}', tex, flags=re.DOTALL)
tex = re.sub(r'\\hypertarget{.*?}{%?\n\s*\\subsubsection{(.*?)}\\label{.*?}}', r'\\subsubsection{\1}', tex, flags=re.DOTALL)

# Fix figure paths
tex = tex.replace('MA_ROPE_TVT_LATEX/figures/media/', 'figures/')
if os.path.exists('MA_ROPE_TVT_LATEX/figures/MA_ROPE_TVT_LATEX/figures/media'):
    os.system('mv MA_ROPE_TVT_LATEX/figures/MA_ROPE_TVT_LATEX/figures/media/* MA_ROPE_TVT_LATEX/figures/')

# Fix bad UTF-8 characters that latex doesn't like, or replace them
tex = tex.replace('✓', r'\checkmark')
tex = tex.replace('✗', r'$\times$')

# Replace unicode greek with latex math
greek_map = {
    'α': r'$\alpha$', 'β': r'$\beta$', 'γ': r'$\gamma$', 'δ': r'$\delta$', 
    'ε': r'$\varepsilon$', 'ζ': r'$\zeta$', 'η': r'$\eta$', 'θ': r'$\theta$', 
    'ι': r'$\iota$', 'κ': r'$\kappa$', 'λ': r'$\lambda$', 'μ': r'$\mu$', 
    'ν': r'$\nu$', 'ξ': r'$\xi$', 'ο': r'$o$', 'π': r'$\pi$', 
    'ρ': r'$\rho$', 'σ': r'$\sigma$', 'τ': r'$\tau$', 'υ': r'$\upsilon$', 
    'φ': r'$\phi$', 'χ': r'$\chi$', 'ψ': r'$\psi$', 'ω': r'$\omega$',
    'Δ': r'$\Delta$', 'Σ': r'$\Sigma$', '∈': r'$\in$', '≥': r'$\geq$', '≤': r'$\leq$',
    '·': r'$\cdot$'
}
for k, v in greek_map.items():
    tex = tex.replace(k, v)

with open('MA_ROPE_TVT_LATEX/main.tex', 'w', encoding='utf-8') as f:
    f.write(tex)
