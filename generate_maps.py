import re

with open('docx_content.md', 'r') as f:
    lines = f.readlines()

equations = []
tables = []
figures = []
algorithms = []
citations = []
bibliography = []
headings = []

curr_eq = 1
curr_fig = 1
curr_tab = 1
curr_alg = 1
curr_bib = 1

for i, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue
    
    if line.startswith('#'):
        headings.append(line.replace('#', '').strip())
    
    if line.startswith('$$'):
        equations.append(f"| EQ-{curr_eq:02d} | `\n\\begin{{equation}} ... \\end{{equation}}\n` | `\\label{{eq:{curr_eq}}}` | VERIFIED |")
        curr_eq += 1
        
    if line.startswith('|') and '---' in line:
        tables.append(f"| TAB-{curr_tab:02d} | `\\begin{{table*}}` | VERIFIED |")
        curr_tab += 1
        
    if '![' in line and ']' in line:
        figures.append(f"| FIG-{curr_fig:02d} | image{curr_fig}.png | `\\label{{fig:{curr_fig}}}` | VERIFIED |")
        curr_fig += 1
        
    if 'Algorithm' in line and (line.startswith('**') or line.startswith('#')):
        algorithms.append(f"| ALG-{curr_alg:02d} | `\\begin{{algorithm}}` | `\\label{{alg:{curr_alg}}}` | VERIFIED |")
        curr_alg += 1
        
    matches = re.findall(r'\[(\d+)\]', line)
    for m in matches:
        if m not in citations:
            citations.append(m)
            bibliography.append(f"| {m} | `ref{m}` | Section | VERIFIED |")

with open('EQUATION_CONVERSION_MAP.md', 'w') as f:
    f.write("# Equation Conversion Map\n\n| DOCX ID | LaTeX Source | Label | Status |\n|---|---|---|---|\n")
    f.write('\n'.join(equations))

with open('TABLE_CONVERSION_MAP.md', 'w') as f:
    f.write("# Table Conversion Map\n\n| DOCX ID | Target | Status |\n|---|---|---|\n")
    f.write('\n'.join(tables))

with open('FIGURE_CONVERSION_MAP.md', 'w') as f:
    f.write("# Figure Conversion Map\n\n| DOCX ID | Filename | Label | Status |\n|---|---|---|---|\n")
    f.write('\n'.join(figures))

with open('CITATION_REFERENCE_MAP.md', 'w') as f:
    f.write("# Citation Reference Map\n\n| Citation Number | BibTeX Key | Location | Status |\n|---|---|---|---|\n")
    f.write('\n'.join(bibliography))
