with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'r') as f:
    text = f.read()

# Line 87
text = text.replace(r'delivere$d_{on}$_time', r'\textit{delivered\_on\_time}')
text = text.replace(r'delivere$d_{late}$', r'\textit{delivered\_late}')
text = text.replace(r'no$t_{delivered}$', r'\textit{not\_delivered}')
text = text.replace(r'\textit{\textit{delivered\_on\_time}}', r'\textit{delivered\_on\_time}')
text = text.replace(r'\textit{\textit{delivered\_late}}', r'\textit{delivered\_late}')
text = text.replace(r'\textit{\textit{not\_delivered}}', r'\textit{not\_delivered}')

# Line 99 & 149
text = text.replace(r'$n_{rx}$_o$n_{time}$/$n_{tx}$', r'$n_{rx\_on\_time}/n_{tx}$')
text = text.replace(r'comput$e_{latency}$_breakdown', r'compute\_latency\_breakdown')

with open('MA_ROPE_TVT_LATEX/sections/related_work.tex', 'w') as f:
    f.write(text)
