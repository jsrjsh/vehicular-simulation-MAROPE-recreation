"""One-shot restyle of tables/*.tex: booktabs rules, no resizebox, readable font. Cell content is never touched."""
import re,glob
WIDE={'table_08_literature','table_09_rat_physical','table_11_hyperparameters'}   # span both columns
SMALL={'table_13_packet_stats','table_14_deadline_analysis','table_10_dual_utility','table_02_action_space'}  # denser -> \scriptsize
for p in sorted(glob.glob('tables/table_*.tex')):
    name=p.split('/')[-1][:-4]; s=open(p).read()
    if 'booktabs-restyled' in s: continue
    s=re.sub(r'\\resizebox\{\\columnwidth\}\{!\}\{%\n','',s)
    s=re.sub(r'\\end\{tabular\}%\n\}\n','\\\\end{tabular}\n',s)
    wide=name in WIDE
    env='table*' if wide else 'table'
    s=re.sub(r'\\begin\{table\*?\}\[[^\]]*\]','\\\\begin{%s}[t]'%env,s); s=s.replace('\\end{table}','\\end{%s}'%env) if env=='table' else re.sub(r'\\end\{table\*?\}','\\\\end{table*}',s)
    # column spec: drop vertical bars
    s=re.sub(r'(\\begin\{tabular\}\{)([^}]*)\}',lambda m:m.group(1)+m.group(2).replace('|','')+'}',s)
    s=re.sub(r'\\multicolumn\{(\d+)\}\{\|c\|\}',r'\\multicolumn{\1}{c}',s)
    lines=s.split('\n'); idx=[i for i,l in enumerate(lines) if l.strip()=='\\hline']
    for n,i in enumerate(idx):
        lines[i]='\\toprule' if n==0 else '\\bottomrule' if n==len(idx)-1 else '\\midrule'
    # no rule directly after a multicolumn sub-header row
    out=[]
    for i,l in enumerate(lines):
        if l=='\\midrule' and out and out[-1].lstrip().startswith('\\multicolumn'): continue
        out.append(l)
    s='\n'.join(out)
    fs='\\scriptsize' if name in SMALL else '\\footnotesize'
    tc='2pt' if name in SMALL else '3pt'
    s=s.replace('\\centering','\\centering\n%% booktabs-restyled\n%s\n\\setlength{\\tabcolsep}{%s}\n\\renewcommand{\\arraystretch}{1.15}'%(fs,tc),1)
    open(p,'w').write(s)
