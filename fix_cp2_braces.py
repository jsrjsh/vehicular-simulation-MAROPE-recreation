import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix the math error \sigma^2_r$ needs to be properly enclosed as $\sigma^2_r$
# The string currently is N(0,$\sigma$^2_r$)
text = text.replace(r'N(0,$\sigma$^2_r$)', r'N(0, $\sigma^2_r$)')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

