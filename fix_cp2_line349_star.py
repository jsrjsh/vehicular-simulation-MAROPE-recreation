import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Replace star
text = text.replace('★', r'$\star$')

# Fix line 349
text = text.replace(r'tabl$e_{vehicle}$_density.csv', r'table\_vehicle\_density.csv')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

