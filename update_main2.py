with open('MA_ROPE_TVT_LATEX/main.tex', 'r') as f:
    text = f.read()

if r'\input{sections/experiments}' not in text:
    text = text.replace(r'\input{sections/algorithm_design}', '\\input{sections/algorithm_design}\n\\input{sections/experiments}')

with open('MA_ROPE_TVT_LATEX/main.tex', 'w') as f:
    f.write(text)

