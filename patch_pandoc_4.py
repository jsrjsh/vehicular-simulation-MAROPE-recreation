with open('MA_ROPE_TVT_LATEX/main.tex', 'r', encoding='utf-8') as f:
    tex = f.read()

preamble = r"""\documentclass[journal,10pt,twocolumn]{IEEEtran}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{siunitx}
\usepackage{cite}
\usepackage{hyperref}
\usepackage{cleveref}
\usepackage{longtable}
"""

parts = tex.split(r'\begin{document}', 1)
tex = preamble + "\n\\begin{document}\n" + parts[1]

with open('MA_ROPE_TVT_LATEX/main.tex', 'w', encoding='utf-8') as f:
    f.write(tex)

