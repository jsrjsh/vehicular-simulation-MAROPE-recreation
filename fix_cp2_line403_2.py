with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

text = text.replace(r'n_$\rho$', r'$n_{\rho}$')
text = text.replace(r'n_$\rho$=2', r'$n_{\rho}=2$')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

