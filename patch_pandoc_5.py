import re
with open('MA_ROPE_TVT_LATEX/main.tex', 'r', encoding='utf-8') as f:
    tex = f.read()

tex = tex.replace(r'\begin{longtable}', r'\begin{table*}' + '\n' + r'\begin{tabular}')
tex = tex.replace(r'\end{longtable}', r'\end{tabular}' + '\n' + r'\end{table*}')
tex = re.sub(r'\\endhead', '', tex)
tex = re.sub(r'\\endfirsthead', '', tex)

with open('MA_ROPE_TVT_LATEX/main.tex', 'w', encoding='utf-8') as f:
    f.write(tex)

