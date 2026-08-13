import os
import re

terms = [
    "Original Authors", "This is the abstract", "dummy", 
    "placeholder", "TODO", "TBD", "lorem", "sample"
]

results = []
count = 0

for root, dirs, files in os.walk('MA_ROPE_TVT_LATEX'):
    for file in files:
        if file.endswith('.tex') or file.endswith('.md') or file.endswith('.bib'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        for term in terms:
                            if term.lower() in line.lower():
                                results.append(f"{path}:{i+1}: MATCH '{term}': {line.strip()}")
                                count += 1
            except:
                pass

with open('PLACEHOLDER_SCAN_CP1.txt', 'w') as f:
    f.write('\n'.join(results))
    
print(f"PLACEHOLDER_MATCHES={count}")
