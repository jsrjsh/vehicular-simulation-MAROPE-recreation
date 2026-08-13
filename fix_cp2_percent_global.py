import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Replace any % that is not preceded by a backslash with \%
text = re.sub(r'(?<!\\)%', r'\%', text)
text = text.replace('μ', r'$\mu$')
text = text.replace('λ', r'$\lambda$')
text = text.replace('σ', r'$\sigma$')
text = text.replace('θ', r'$\theta$')
text = text.replace('α', r'$\alpha$')
text = text.replace('β', r'$\beta$')
text = text.replace('γ', r'$\gamma$')
text = text.replace('ρ', r'$\rho$')
text = text.replace('τ', r'$\tau$')
text = text.replace('ε', r'$\epsilon$')
text = text.replace('≥', r'$\geq$')
text = text.replace('≤', r'$\leq$')
text = text.replace('×', r'$\times$')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

