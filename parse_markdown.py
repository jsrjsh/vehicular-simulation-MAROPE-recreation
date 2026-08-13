import re

with open('docx_content.md', 'r') as f:
    lines = f.readlines()

headings = []
paragraphs_per_sec = []
curr_para_count = 0
tables_count = 0
figures_count = 0
equations_count = 0
algorithms_count = 0
citations_count = 0
bib_count = 0
footnotes_count = 0

in_table = False
in_equation = False
in_algorithm = False

for line in lines:
    line = line.strip()
    if not line:
        continue
        
    if line.startswith('#'):
        if headings:
            paragraphs_per_sec.append(curr_para_count)
        headings.append(line)
        curr_para_count = 0
    elif line.startswith('|') and '---' in line:
        tables_count += 1
    elif '![' in line and ']' in line and '(' in line and ')' in line:
        figures_count += 1
    elif line.startswith('$$'):
        equations_count += 1
    elif 'Algorithm' in line and (line.startswith('**') or line.startswith('#')):
        algorithms_count += 1
    elif line.startswith('[') and ']' in line and not line.startswith('!['):
        bib_count += 1
    else:
        curr_para_count += 1
        
    citations_count += len(re.findall(r'\[\d+\]', line))

if headings:
    paragraphs_per_sec.append(curr_para_count)
        
with open('DOCX_CONTENT_INVENTORY.md', 'w') as f:
    f.write("# Manuscript Inventory\n\n")
    f.write("## Headings and Paragraphs\n")
    for i, h in enumerate(headings):
        f.write(f"- {h} ({paragraphs_per_sec[i]} paragraphs)\n")
        
    f.write(f"\n## Objects\n")
    f.write(f"- Tables: {tables_count}\n")
    f.write(f"- Figures (Estimated): {figures_count}\n")
    f.write(f"- Algorithms (Estimated): {algorithms_count}\n")
    f.write(f"- Equations (Estimated): {equations_count}\n")
    f.write(f"- Citations (Estimated): {citations_count}\n")
    f.write(f"- Bibliography Entries: {bib_count}\n")
    f.write(f"- Footnotes: {footnotes_count}\n")
    
    f.write("\n## Mapping Table\n")
    f.write("| Object | Destination LaTeX File | Status |\n")
    f.write("|---|---|---|\n")
    for i, h in enumerate(headings):
        clean_h = h.replace('#', '').strip()
        f.write(f"| Section: {clean_h} | sections/sec_{i:02d}.tex | PENDING |\n")

