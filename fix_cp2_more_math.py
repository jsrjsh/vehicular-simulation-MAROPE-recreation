import re

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

math_map = {
    'μ': r'\mu', 'λ': r'\lambda', 'σ': r'\sigma', 'τ': r'\tau', 
    'θ': r'\theta', 'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 
    'ρ': r'\rho', '∈': r'\in', '−': '-'
}

for k, v in math_map.items():
    text = text.replace(k, f'${v}$')

# Fix nested double math modes if they were created, e.g. $\mu$
text = text.replace('$$', '$')
text = re.sub(r'\$\$(.*?)\$\$', r'$\1$', text)

# Specifically for 1/(\mu_k - \lambda_k)
text = re.sub(r'1/\(\$\\mu\$_k - \$\\lambda\$_k\)', r'$1/(\mu_k - \lambda_k)$', text)

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

