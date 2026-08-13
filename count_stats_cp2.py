import re

with open('docx_content.md', 'r') as f:
    docx_text = f.read()

# Extract Section II from docx_content.md
section_ii_start = docx_text.find('II. RELATED WORK')
section_iii_start = docx_text.find('III. SYSTEM MODEL AND PROBLEM FORMULATION')
docx_section = docx_text[section_ii_start:section_iii_start]

docx_paras = [p for p in docx_section.split('\n\n') if p.strip()]
docx_words = len(re.findall(r'\w+', docx_section))
docx_citations = len(re.findall(r'\[\d+\]|\[\d+\]--\[\d+\]', docx_section))
docx_fig_refs = len(re.findall(r'Fig\.\s*\d+', docx_section, re.IGNORECASE))
docx_tab_refs = len(re.findall(r'Table\s+[IVX]+', docx_section, re.IGNORECASE))

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    latex_section = f.read()

latex_paras = [p for p in latex_section.split('\n\n') if p.strip()]
latex_words = len(re.findall(r'\w+', latex_section))
latex_citations = len(re.findall(r'\[\d+\]|\[\d+\]--\[\d+\]', latex_section))
latex_fig_refs = len(re.findall(r'Fig\.\s*\d+', latex_section, re.IGNORECASE))
latex_tab_refs = len(re.findall(r'Table\s+[IVX]+', latex_section, re.IGNORECASE))

print("--- Source DOCX ---")
print(f"Paragraphs: {len(docx_paras)}")
print(f"Words: {docx_words}")
print(f"Citations: {docx_citations}")
print(f"Fig Refs: {docx_fig_refs}")
print(f"Tab Refs: {docx_tab_refs}")

print("\n--- Generated LaTeX ---")
print(f"Paragraphs: {len(latex_paras)}")
print(f"Words: {latex_words}")
print(f"Citations: {latex_citations}")
print(f"Fig Refs: {latex_fig_refs}")
print(f"Tab Refs: {latex_tab_refs}")
