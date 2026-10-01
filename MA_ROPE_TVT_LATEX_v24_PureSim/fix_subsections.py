import os, glob, re

for f in glob.glob('sections/*.tex'):
    with open(f, 'r') as file:
        content = file.read()
    
    # Replace \subsection*{X. Title} with \subsection{Title}
    content = re.sub(r'\\subsection\*\{[A-Z]\.\s*(.*?)\}', r'\\subsection{\1}', content)
    
    with open(f, 'w') as file:
        file.write(content)
