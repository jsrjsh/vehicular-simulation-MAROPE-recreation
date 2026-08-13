import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix the apostrophe escaping issue in math mode which breaks XeTeX (a\')
text = text.replace(r'a\'', "a'")
text = text.replace(r'\{', '{')
text = text.replace(r'\}', '}')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

