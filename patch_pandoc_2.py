import re

with open('MA_ROPE_TVT_LATEX/main.tex', 'r', encoding='utf-8') as f:
    tex = f.read()

# Remove unicode-math
tex = tex.replace(r'\usepackage{unicode-math}', '')
tex = tex.replace(r'\setmathfont{Latin Modern Math}', '')

# If pandoc inserted any \includegraphics{MA_ROPE_TVT_LATEX/figures/media/image...} let's replace it
tex = tex.replace('MA_ROPE_TVT_LATEX/figures/media/', 'figures/')

with open('MA_ROPE_TVT_LATEX/main.tex', 'w', encoding='utf-8') as f:
    f.write(tex)

