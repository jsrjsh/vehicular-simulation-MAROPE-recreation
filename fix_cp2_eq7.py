import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix equation 7
text = text.replace(r"> \textit{y = r + $\gamma$ \cdot  $Q_{tgt}$(s\', argmax\_{a'} $Q_{online}$(s\', a'))} (7)",
r"""\begin{equation}
y = r + \gamma \cdot Q_{tgt}(s', \arg\max_{a'} Q_{online}(s', a')) \tag{7}
\end{equation}""")

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

