with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    lines = f.readlines()

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.writelines(lines[:34])

