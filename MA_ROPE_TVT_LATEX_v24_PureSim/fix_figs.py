import re

with open('sections/methodology.tex', 'r') as f:
    text = f.read()

# find figure
fig_match = re.search(r'\\begin\{figure\}.*?\\end\{figure\}', text, re.DOTALL)
if fig_match:
    fig_text = fig_match.group(0)
    text = text.replace(fig_text, '')
    text += '\n\n' + fig_text

with open('sections/methodology.tex', 'w') as f:
    f.write(text)
