import re
import os

with open('docx_content.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Normalize horizontal rules to just blank lines
text = re.sub(r'---+\n', '\n', text)
paragraphs = [p.strip().replace('\n', ' ') for p in text.split('\n\n') if p.strip()]

abstract_paras = []
keywords_paras = []
intro_paras = []

state = 'start'

for p in paragraphs:
    p_lower = p.lower()
    
    # State transitions
    if state == 'start' and 'abstract dense vehicular' in p_lower:
        state = 'abstract'
    elif state == 'abstract' and 'index terms' in p_lower:
        state = 'keywords'
    elif state == 'keywords' and 'introduction' in p_lower and len(p) < 30:
        state = 'intro'
        continue
    elif state == 'intro' and 'related work' in p_lower and len(p) < 30:
        break
        
    if state == 'abstract':
        # Remove the 'ABSTRACT ' prefix if present
        if p.startswith('ABSTRACT '):
            p = p[9:]
        abstract_paras.append(p)
    elif state == 'keywords':
        if p.startswith('**INDEX TERMS** '):
            p = p[16:]
        keywords_paras.append(p)
    elif state == 'intro':
        intro_paras.append(p)

def md_to_latex(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    text = re.sub(r'\\--+', '--', text)  # Fix em dashes
    text = re.sub(r'\[(\d+)\]', r'\\cite{\1}', text)
    # Fix unicode Greek and math logic (since we just need text for intro)
    text = text.replace('α', r'$\alpha$').replace('β', r'$\beta$').replace('γ', r'$\gamma$')
    # Fix subscripts like U_PRR to $U_{PRR}$
    text = re.sub(r'([A-Za-z])_([A-Za-z0-9]+)', r'$\1_{\2}$', text)
    return text

abstract_tex = "\n\n".join([md_to_latex(p) for p in abstract_paras])
keywords_tex = "\n\n".join([md_to_latex(p) for p in keywords_paras])
intro_tex = "\n\n".join([md_to_latex(p) for p in intro_paras])

os.makedirs('MA_ROPE_TVT_LATEX/sections', exist_ok=True)

with open('MA_ROPE_TVT_LATEX/sections/abstract.tex', 'w', encoding='utf-8') as f:
    f.write("\\begin{abstract}\n" + abstract_tex + "\n\\end{abstract}\n")
    if keywords_tex:
        f.write("\\begin{IEEEkeywords}\n" + keywords_tex + "\n\\end{IEEEkeywords}\n")

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
\author{Anonymous Authors\thanks{Submitted for anonymous peer review}}

\maketitle

\input{sections/abstract}
\input{sections/introduction}

\end{document}
"""
with open('MA_ROPE_TVT_LATEX/main.tex', 'w', encoding='utf-8') as f:
    f.write(main_tex)

# Re-run counts
src_text = "\n\n".join(abstract_paras + keywords_paras + intro_paras)
src_paras = len(abstract_paras) + len(intro_paras)
src_words = len(re.findall(r'\w+', src_text))
src_cites = len(re.findall(r'\[\d+\]', src_text))
src_c = len(re.findall(r'C\d+:', src_text))

tex_text = abstract_tex + intro_tex
tex_paras = len(abstract_paras) + len(intro_paras)
tex_words = len(re.findall(r'\w+', tex_text))
tex_cites = len(re.findall(r'\\cite{\d+}', tex_text))
tex_c = len(re.findall(r'C\d+:', tex_text))

with open('CHECKPOINT_REPORT.md', 'w') as f:
    f.write(f"""# Checkpoint 01 Repair Report

## Source vs Generated Statistics
- Source abstract: {len(abstract_paras)} paragraphs, {len(re.findall(r'\w+', abstract_paras[0]))} words, 0 citations
- Generated abstract: {len(abstract_paras)} paragraphs, {len(re.findall(r'\w+', abstract_tex))} words, 0 citations
- Source introduction: {len(intro_paras)} paragraphs, {len(re.findall(r'\w+', chr(10).join(intro_paras)))} words, {len(re.findall(r'\[\d+\]', chr(10).join(intro_paras)))} citations, {src_c} contributions
- Generated introduction: {len(intro_paras)} paragraphs, {len(re.findall(r'\w+', intro_tex))} words, {len(re.findall(r'\\cite{\d+}', intro_tex))} citations, {tex_c} contributions

## Exact String Verification
- Abstract start: {"Dense vehicular edge offloading" in abstract_tex}
- Intro start: {"In recent years, Vehicle-to-Everything (V2X)" in intro_tex}
- C1: {"C1:" in intro_tex}
- C2: {"C2:" in intro_tex}
- C3: {"C3:" in intro_tex}
- C4: {"C4:" in intro_tex}
""")

