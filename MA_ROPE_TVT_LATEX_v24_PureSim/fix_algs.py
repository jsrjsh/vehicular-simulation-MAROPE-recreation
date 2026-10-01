import re

with open('sections/algorithm_design.tex', 'r') as f:
    text = f.read()

# find algorithm
alg_match = re.search(r'\\begin\{algorithm\}.*?\\end\{algorithm\}', text, re.DOTALL)
if alg_match:
    alg_text = alg_match.group(0)
    text = text.replace(alg_text, '')
    text += '\n\n' + alg_text

with open('sections/algorithm_design.tex', 'w') as f:
    f.write(text)
