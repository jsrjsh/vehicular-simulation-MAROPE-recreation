import os
import re

base_dir = '/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/MA_ROPE_TVT_LATEX_v24_PureSim/sections'

# 1. introduction.tex
with open(os.path.join(base_dir, 'introduction.tex'), 'r') as f:
    intro = f.read()

# Replace C1, C2, C3, C4 correctly
intro = re.sub(r'\\item\s*\\textbf\{C1:.*?\}\s*', 'First, ', intro)
intro = re.sub(r'\\item\s*\\textbf\{C2:.*?\}\s*', 'Second, ', intro)
intro = re.sub(r'\\item\s*\\textbf\{C3:.*?\}\s*', 'Third, ', intro)
intro = re.sub(r'\\item\s*\\textbf\{C4:.*?\}\s*', 'Finally, ', intro)
intro = intro.replace('\\begin{itemize}', '')
intro = intro.replace('\\end{itemize}', '')

# Wait, previously I replaced C1 but maybe not C2, C3, C4. Let's fix C1 too if it's there.
# But C1 was already replaced in my previous script? Let's check `grep C1` output. The grep above didn't show C1.
# But it did show C2, C3, C4.
# If C1 was replaced with "The first contribution is...", let's change it to "First, ".
intro = intro.replace('The first contribution is the joint optimization of multi-RAT selection and partial computation offloading under shared queue contention. We formulate', 'First, we formulate')

with open(os.path.join(base_dir, 'introduction.tex'), 'w') as f:
    f.write(intro)


# 2. system_model.tex (Section III)
# Reorder to A, B, C, D, E
# Wait, the user said: "currently shows B, A, C, E, D". 
# Ah! Let's read system_model.tex to see what the exact text order is.
