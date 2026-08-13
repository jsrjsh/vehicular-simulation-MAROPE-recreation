with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

text = text.replace(r'\textbf{n_$\rho$}', r'\textbf{$n_{\rho}$}')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

