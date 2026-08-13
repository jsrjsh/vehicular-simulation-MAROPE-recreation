with open('MA_ROPE_TVT_LATEX/main.tex', 'r') as f:
    text = f.read()

text = text.replace(r'\input{sections/related_work}', '\\input{sections/related_work}\n\\input{sections/system_model}')

with open('MA_ROPE_TVT_LATEX/main.tex', 'w') as f:
    f.write(text)

