with open('MA_ROPE_TVT_LATEX/main.tex', 'r') as f:
    text = f.read()

if r'\input{sections/conclusion}' not in text:
    text = text.replace(r'\input{sections/results_part2}', '\\input{sections/results_part2}\n\\input{sections/conclusion}')

with open('MA_ROPE_TVT_LATEX/main.tex', 'w') as f:
    f.write(text)

