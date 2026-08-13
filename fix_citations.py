import os
import re

key_map = {
    '1': 'bo2025',
    '2': 'syed2025',
    '3': 'shao2025',
    '4': 'wu2021',
    '5': 'jing2019',
    '6': 'yun2022',
    '7': 'lowe2017',
    '8': 'guo2026',
    '9': 'yacheur2023',
    '10': 'mcmahan2017',
    '11': 'luo2025',
    '12': 'ieee80211ax',
    '13': '3gpp2022',
    '14': 'mao2017',
    '15': 'molina2017'
}

base_dir = 'MA_ROPE/MASTER/MA_ROPE_MASTER_v21'

# 1. Update references.bib
with open(os.path.join(base_dir, 'references.bib'), 'r') as f:
    bib = f.read()

for old_key, new_key in key_map.items():
    # Replace @article{3, with @article{shao2025,
    bib = re.sub(rf'@(article|inproceedings|misc)\{{{old_key},', rf'@\1{{{new_key},', bib)

with open(os.path.join(base_dir, 'references.bib'), 'w') as f:
    f.write(bib)

# 2. Update .tex files in sections/
tex_dir = os.path.join(base_dir, 'sections')
for fname in os.listdir(tex_dir):
    if not fname.endswith('.tex'): continue
    path = os.path.join(tex_dir, fname)
    with open(path, 'r') as f:
        text = f.read()
    
    # First, replace existing \cite{X}
    for old_key, new_key in key_map.items():
        text = re.sub(rf'\\cite\{{{old_key}\}}', rf'\\cite{{{new_key}}}', text)
    
    # Now, replace manual [X] or [X]--[Y] 
    # specific rules for related_work.tex:
    if fname == 'related_work.tex':
        # [5]--[7] -> \cite{jing2019,yun2022,lowe2017}
        text = text.replace('[5]--[7]', r'~\cite{jing2019,yun2022,lowe2017}')
        
        # [3]
        text = text.replace('CoopEC [3]', r'CoopEC~\cite{shao2025}')
        text = text.replace('Shao 2025 [3]', r'Shao 2025~\cite{shao2025}')
        
        # [4]
        text = text.replace('UCB [4]', r'UCB~\cite{wu2021}')
        text = text.replace('Wu 2021 [4]', r'Wu 2021~\cite{wu2021}')
        
        # [8]
        text = text.replace('Guo et al. [8]', r'Guo et al.~\cite{guo2026}')
        text = text.replace('Guo 2026 [8]', r'Guo 2026~\cite{guo2026}')
        
        # [9]
        text = text.replace('Yacheur et al. [9]', r'Yacheur et al.~\cite{yacheur2023}')
        text = text.replace('Yacheur 2023 [9]', r'Yacheur 2023~\cite{yacheur2023}')
        
    with open(path, 'w') as f:
        f.write(text)

print("Citations converted successfully.")
