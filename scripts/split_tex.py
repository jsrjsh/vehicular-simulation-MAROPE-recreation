import os
import re

def parse_and_split():
    with open('v21_text.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = {
        'abstract.tex': [],
        'introduction.tex': [],
        'related_work.tex': [],
        'system_model.tex': [],
        'methodology.tex': [],
        'experiments.tex': [],
        'results.tex': [],
        'conclusion.tex': []
    }
    
    current_section = None
    
    # Very crude mapping based on standard paper headings
    # Needs manual refinement after.
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        upper_line = line_clean.upper()
        
        if upper_line.startswith('ABSTRACT'):
            current_section = 'abstract.tex'
        elif upper_line.startswith('I. INTRODUCTION'):
            current_section = 'introduction.tex'
            sections[current_section].append(r'\section{Introduction}')
            continue
        elif upper_line.startswith('II. RELATED WORK'):
            current_section = 'related_work.tex'
            sections[current_section].append(r'\section{Related Work}')
            continue
        elif upper_line.startswith('III. SYSTEM MODEL'):
            current_section = 'system_model.tex'
            sections[current_section].append(r'\section{System Model}')
            continue
        elif upper_line.startswith('IV. '):
            # Problem formulation / Methodology
            current_section = 'methodology.tex'
            sections[current_section].append(r'\section{Methodology}')
            continue
        elif upper_line.startswith('V. EXPERIMENTS AND RESULTS'):
            current_section = 'experiments.tex'
            sections[current_section].append(r'\section{Experiments and Results}')
            continue
        elif upper_line.startswith('VI. CONCLUSION'):
            current_section = 'conclusion.tex'
            sections[current_section].append(r'\section{Conclusion}')
            continue
        elif upper_line.startswith('REFERENCES'):
            current_section = None
            continue
            
        if current_section:
            # Basic text escaping
            escaped_line = line_clean.replace('%', r'\%').replace('&', r'\&').replace('$', r'\$').replace('_', r'\_')
            sections[current_section].append(escaped_line)

    for filename, content in sections.items():
        if content:
            out_path = os.path.join('MA_ROPE_TVT_LATEX', 'sections', filename)
            with open(out_path, 'w', encoding='utf-8') as out_f:
                if filename == 'abstract.tex':
                    out_f.write(r'\begin{abstract}' + '\n')
                    out_f.write('\n\n'.join(content).replace('ABSTRACT ', ''))
                    out_f.write('\n' + r'\end{abstract}' + '\n')
                else:
                    out_f.write('\n\n'.join(content))

if __name__ == "__main__":
    parse_and_split()
