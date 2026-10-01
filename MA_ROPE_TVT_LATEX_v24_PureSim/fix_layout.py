import re

# Fix 1: Equation split in sections/system_model.tex
with open('sections/system_model.tex', 'r') as f:
    content = f.read()

eq_original = r"""L_{total} = L_{prop} + \rho \cdot L_{tx} + \max(\rho \cdot L_{remote} + L_{rx} + L_{prop}, (1-\rho) \cdot L_{local}) + L_{queue}"""
eq_replacement = r"""\begin{split}
L_{total} =& L_{prop} + \rho \cdot L_{tx} \\
&+ \max(\rho \cdot L_{remote} + L_{rx} + L_{prop}, (1-\rho) \cdot L_{local}) \\
&+ L_{queue}
\end{split}"""

if eq_original in content:
    content = content.replace(eq_original, eq_replacement)
    with open('sections/system_model.tex', 'w') as f:
        f.write(content)
    print("Fixed equation in system_model.tex")

# Fix 2: Remove \newpage
files_with_newpage = [
    'sections/algorithm_design.tex',
    'sections/experiments.tex',
    'sections/methodology.tex'
]
for file in files_with_newpage:
    with open(file, 'r') as f:
        content = f.read()
    if r'\newpage' in content:
        content = content.replace(r'\newpage', '')
        with open(file, 'w') as f:
            f.write(content)
        print(f"Removed \newpage from {file}")

# Fix 3: Fix hyperref in main.tex and add \flushbottom
with open('main.tex', 'r') as f:
    content = f.read()

if r'\usepackage{hyperref}' in content:
    content = content.replace(r'\usepackage{hyperref}', r'\usepackage[hidelinks]{hyperref}')
    print("Fixed hyperref in main.tex")

if r'\flushbottom' not in content:
    content = content.replace(r'\begin{document}', "\\flushbottom\n\\begin{document}")
    print("Added \\flushbottom to main.tex")

with open('main.tex', 'w') as f:
    f.write(content)

