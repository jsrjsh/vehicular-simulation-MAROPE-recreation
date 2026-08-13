with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

text = text.replace('≤', r'$\leq$')
text = text.replace('≥', r'$\geq$')
text = text.replace(r'\>', r'$>$')
text = text.replace('>', r'$>$')
text = text.replace('<', r'$<$')
text = text.replace(r'$n_{rx}$_o$n_{time}$', r'$n_{rx\_on\_time}$')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)
