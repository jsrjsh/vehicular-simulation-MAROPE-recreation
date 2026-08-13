import re
import os

with open('docx_content.md', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'---+\n', '\n', text)
paragraphs = [p.strip().replace('\n', ' ') for p in text.split('\n\n') if p.strip()]

rw_paras = []
state = 'start'

for p in paragraphs:
    p_lower = p.lower()
    
    if state == 'start' and ('related work' in p_lower and len(p) < 30):
        state = 'rw'
        continue
    elif state == 'rw' and ('system model' in p_lower and len(p) < 30):
        break
        
    if state == 'rw':
        rw_paras.append(p)

subsections = []
for p in rw_paras:
    if p.startswith('**A.') or p.startswith('A.'):
        subsections.append(('A', p.replace('**', '').replace('A. ', '').strip()))
    elif p.startswith('**B.') or p.startswith('B.'):
        subsections.append(('B', p.replace('**', '').replace('B. ', '').strip()))
    elif p.startswith('**C.') or p.startswith('C.'):
        subsections.append(('C', p.replace('**', '').replace('C. ', '').strip()))

def md_to_latex(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    text = re.sub(r'\\--+', '--', text)
    text = re.sub(r'\[(\d+)\]', r'\\cite{\1}', text)
    
    # Fix unicode Greek and math logic
    math_map = {
        'α': r'$\alpha$', 'β': r'$\beta$', 'γ': r'$\gamma$', 'ρ': r'$\rho$', '∈': r'$\in$',
        '✓': r'\checkmark{}', '✗': r'$\times$'
    }
    for k, v in math_map.items():
        text = text.replace(k, v)
        
    text = re.sub(r'([A-Za-z])_([A-Za-z0-9]+)', r'$\1_{\2}$', text)
    
    # Remove raw image links if any got caught in the text
    text = re.sub(r'!\[.*?\]\(.*?\)(\{.*?\})?', '', text)
    return text

rw_tex_lines = ["\\section{Related Work}"]
for p in rw_paras:
    if p.startswith('![') or p.startswith('|'):
        continue # skip images and tables for now, they belong in system model or results
        
    clean = p.replace('**', '')
    if clean.startswith('A.'):
        rw_tex_lines.append("\\subsection{" + clean[2:].strip() + "}")
    elif clean.startswith('B.'):
        rw_tex_lines.append("\\subsection{" + clean[2:].strip() + "}")
    elif clean.startswith('C.'):
        rw_tex_lines.append("\\subsection{" + clean[2:].strip() + "}")
    else:
        rw_tex_lines.append(md_to_latex(p))

rw_tex = "\n\n".join([t for t in rw_tex_lines if t.strip()])

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w', encoding='utf-8') as f:
    f.write(rw_tex + "\n")

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
\author{Anonymous Authors\thanks{Submitted for anonymous peer review}}

\maketitle

\input{sections/abstract}
\input{sections/introduction}
\input{sections/related_work}

\end{document}
"""
with open('MA_ROPE_TVT_LATEX/main.tex', 'w', encoding='utf-8') as f:
    f.write(main_tex)

# Counts
src_text = "\n\n".join(rw_paras)
src_cites = len(re.findall(r'\[\d+\]', src_text))
src_words = len(re.findall(r'\w+', src_text))
src_paras = len(rw_paras)
src_subsections = len(subsections)

tex_text = rw_tex
tex_cites = len(re.findall(r'\\cite{\d+}', tex_text))
tex_words = len(re.findall(r'\w+', tex_text))
# subtract 1 for the \section header, subtract subsections
tex_paras = len(rw_tex_lines) - 1 - len(subsections)

fig_ref = len(re.findall(r'Fig\. \d+', src_text, re.IGNORECASE)) + len(re.findall(r'Figure \d+', src_text, re.IGNORECASE))
tab_ref = len(re.findall(r'Table \w+', src_text, re.IGNORECASE))

print(f"SRC_WORDS={src_words}")
print(f"TEX_WORDS={tex_words}")
print(f"SRC_PARAS={src_paras}")
print(f"TEX_PARAS={tex_paras}")
print(f"SRC_CITES={src_cites}")
print(f"TEX_CITES={tex_cites}")
print(f"SUBSECTIONS={src_subsections}")
print(f"FIG_REFS={fig_ref}")
print(f"TAB_REFS={tab_ref}")
print(f"TABLE_1_REF={'table i' in src_text.lower()}")
print(f"FIG_1_REF={'fig. 1' in src_text.lower() or 'figure 1' in src_text.lower()}")
print(f"FIG_2_REF={'fig. 2' in src_text.lower() or 'figure 2' in src_text.lower()}")

