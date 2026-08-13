with open('MA_ROPE_TVT_LATEX/main.tex', 'r') as f:
    text = f.read()

if r'\usepackage{algorithm}' not in text:
    text = text.replace(r'\usepackage{cleveref}', '\\usepackage{cleveref}\n\\usepackage{algorithm}\n\\usepackage{algorithmic}')

if r'\input{sections/algorithm_design}' not in text:
    text = text.replace(r'\input{sections/system_model}', '\\input{sections/system_model}\n\\input{sections/algorithm_design}')

with open('MA_ROPE_TVT_LATEX/main.tex', 'w') as f:
    f.write(text)

