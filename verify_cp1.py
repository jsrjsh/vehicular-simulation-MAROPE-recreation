import re
import os

with open('docx_content.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

abstract_lines = []
intro_lines = []
state = None

for line in lines:
    clean = line.strip()
    if clean.lower().startswith('# abstract') or clean.lower() == 'abstract':
        state = 'abstract'
        continue
    if clean.lower().startswith('# 1. introduction') or clean.lower() == '# i. introduction':
        state = 'intro'
        continue
    if clean.lower().startswith('# 2. related work') or clean.lower() == '# ii. related work':
        break
    if state == 'abstract' and clean: abstract_lines.append(clean)
    elif state == 'intro' and clean: intro_lines.append(clean)

src_text = "\n".join(abstract_lines + intro_lines)
src_paras = len(abstract_lines) + len(intro_lines)
src_words = len(re.findall(r'\w+', src_text))
src_cites = len(re.findall(r'\[\d+\]', src_text))

with open('MA_ROPE_TVT_LATEX/sections/abstract.tex', 'r') as f:
    tex_abs = f.read()
with open('MA_ROPE_TVT_LATEX/sections/introduction.tex', 'r') as f:
    tex_intro = f.read()
    
tex_text = tex_abs + tex_intro
tex_paras = len([p for p in tex_text.split('\n\n') if p.strip() and not p.strip().startswith('\\begin') and not p.strip().startswith('\\end') and not p.strip().startswith('\\section')])
tex_words = len(re.findall(r'\w+', tex_text))
tex_cites = len(re.findall(r'\\cite{\d+}', tex_text))

print(f"SRC: paras={src_paras}, words={src_words}, cites={src_cites}")
print(f"TEX: paras={tex_paras}, words={tex_words}, cites={tex_cites}")

# placeholders
terms = ["Original Authors", "Anonymous Authors", "placeholder", "dummy", "TODO", "TBD", "This is the abstract", "sample", "example", "lorem"]
found = []
for file in ['MA_ROPE_TVT_LATEX/main.tex', 'MA_ROPE_TVT_LATEX/sections/abstract.tex', 'MA_ROPE_TVT_LATEX/sections/introduction.tex']:
    with open(file, 'r') as f:
        content = f.read()
        for t in terms:
            if t.lower() in content.lower():
                found.append((file, t))
print("PLACEHOLDERS:", found)

