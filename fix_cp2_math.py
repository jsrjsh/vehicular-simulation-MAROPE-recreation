import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix U+2212 minus sign
text = text.replace('−', '-')
# Fix \theta_r
text = text.replace(r'$\theta$_r', r'$\theta_r$')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

