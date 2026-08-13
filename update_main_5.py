with open('MA_ROPE_TVT_LATEX/main.tex', 'r') as f:
    text = f.read()

if r'\bibliography{references}' not in text:
    text = text.replace(r'\end{document}', '\\bibliographystyle{IEEEtran}\n\\bibliography{references}\n\\end{document}')

with open('MA_ROPE_TVT_LATEX/main.tex', 'w') as f:
    f.write(text)

