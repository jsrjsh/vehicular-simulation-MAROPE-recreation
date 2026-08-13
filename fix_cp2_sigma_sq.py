import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix the missing sigma squared parsing issue which XeTeX crashes on (²_r)
text = text.replace('²_r', r'^2_r$')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

