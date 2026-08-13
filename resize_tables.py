with open('MA_ROPE_TVT_LATEX/sections/system_model.tex', 'r') as f:
    text = f.read()

import re
text = re.sub(r'(\\begin{tabular}.*?\\end{tabular})', r'\\resizebox{\\columnwidth}{!}{%\n\g<1>%\n}', text, flags=re.DOTALL)

with open('MA_ROPE_TVT_LATEX/sections/system_model.tex', 'w') as f:
    f.write(text)

