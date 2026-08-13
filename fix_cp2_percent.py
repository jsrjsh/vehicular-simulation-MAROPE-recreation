import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix percentage sign
text = text.replace('70%', r'70\%')

# Fix dot
text = text.replace('·', r'\cdot ')

# Fix equation 8
text = text.replace(r'> \textit{$w_{global}$ = \Sigma_i ($n_{i}$ / N) \cdot  $w_{i}$, participation $\geq$ 70\%} (8)',
r"""\begin{equation}
w_{global} = \sum_i \frac{n_{i}}{N} \cdot w_{i}, \quad \text{participation} \geq 70\% \tag{8}
\end{equation}""")

# Clean up pseudocode block (Algorithm 1)
text = text.replace('> Require:', 'Require:')
text = text.replace('> >', '')
text = text.replace('> ', '')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

