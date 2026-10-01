import os
import re

tables_dir = 'tables'

for filename in os.listdir(tables_dir):
    if not filename.endswith('.tex'):
        continue
        
    filepath = os.path.join(tables_dir, filename)
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Change \begin{table}[...] to \begin{table}[h!]
    content = re.sub(r'\\begin\{table\}\[.*?\]', r'\\begin{table}[h!]', content)
    content = re.sub(r'\\begin\{table\*\}\[.*?\]', r'\\begin{table*}[h!]', content)
    if '\\begin{table}' in content and '\\begin{table}[' not in content:
        content = content.replace('\\begin{table}', '\\begin{table}[h!]')
    
    # 2. Replace booktabs with hline
    content = content.replace('\\toprule', '\\hline')
    content = content.replace('\\midrule', '\\hline')
    content = content.replace('\\bottomrule', '\\hline')
    
    # 3. Add vertical bars to tabular if missing
    def fix_tabular(match):
        alignment = match.group(1)
        # Remove existing vertical bars
        alignment = alignment.replace('|', '')
        # Add vertical bars around every character that is l, c, r, or p{...}
        # Actually a simple way is just replace l, c, r with |l|, |c|, |r| and fix duplicates
        fixed = ""
        for char in alignment:
            if char in 'lcr':
                fixed += f"|{char}"
            else:
                fixed += char
        if fixed and not fixed.endswith('|'):
            fixed += '|'
        return f"\\begin{{tabular}}{{{fixed}}}"

    content = re.sub(r'\\begin\{tabular\}\{(.*?)\}', fix_tabular, content)
    
    # 4. Wrap with resizebox if not already
    if '\\resizebox' not in content:
        content = re.sub(r'(\\begin\{tabular\}.*?\\end\{tabular\})', r'\\resizebox{\\columnwidth}{!}{%\n\1%\n}', content, flags=re.DOTALL)

    with open(filepath, 'w') as f:
        f.write(content)
        
    print(f"Formatted {filename}")

