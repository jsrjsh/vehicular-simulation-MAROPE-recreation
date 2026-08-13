import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix Eq 6 which looks like:
# > *$\rho$_{r}* = min(1.0, SIN$R_{lin}$\[r\] / \Sigma SIN$R_{lin}$\[all\]) (6)
# First fix \Sigma
text = text.replace('Σ', r'\Sigma')

# Actually, let's just properly format Equation 6 if we can find it
# Search for the line containing `(6)`
lines = text.split('\n')
for i, line in enumerate(lines):
    if '(6)' in line and 'SIN' in line:
        lines[i] = r"""\begin{equation}
\rho_{r} = \min(1.0, \frac{SINR_{lin}[r]}{\sum SINR_{lin}[all]}) \tag{6}
\end{equation}"""

text = '\n'.join(lines)

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

