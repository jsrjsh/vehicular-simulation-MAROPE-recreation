with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Fix verbatim block symbols
text = text.replace('τ=0.70', 'tau=0.70')
text = text.replace('ε-greedy', 'epsilon-greedy')
text = text.replace('≥ τ', '>= tau')
text = text.replace('Σ', 'SUM')

# Fix line 189
text = text.replace(r'forma$t_{packet}$_stat$s_{table}$()', r'format\_packet\_stats\_table()')

# I also see `comput$e_{latency}$_breakdown` may still be present? I fixed it earlier. Let's just be sure.
text = text.replace(r'comput$e_{latency}$_breakdown', r'compute\_latency\_breakdown')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)

