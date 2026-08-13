with open('MA_ROPE_TVT_LATEX/main.tex', 'r') as f:
    text = f.read()

if r'\input{sections/results_part1}' not in text:
    text = text.replace(r'\input{sections/experiments}', '\\input{sections/experiments}\n\\input{sections/results_part1}\n\\input{sections/results_part2}')

with open('MA_ROPE_TVT_LATEX/main.tex', 'w') as f:
    f.write(text)

