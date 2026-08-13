import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix the tilde character which XeTeX parses as a hard space, breaking math mode
# N(0, \sigma^2_r)
text = text.replace(r'\~', r'$\sim$')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

