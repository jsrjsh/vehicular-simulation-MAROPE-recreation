with open('sections/methodology.tex', 'r') as f:
    c = f.read()
if '\\clearpage' not in c:
    with open('sections/methodology.tex', 'w') as f:
        f.write('\\clearpage\n' + c)

with open('sections/algorithm_design.tex', 'r') as f:
    c = f.read()
if '\\clearpage' not in c:
    with open('sections/algorithm_design.tex', 'w') as f:
        f.write('\\clearpage\n' + c)
