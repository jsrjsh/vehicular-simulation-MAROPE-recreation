"""Second pass: tabular -> tabularx (full column width, wrapping X columns, weighted)."""
import re,glob
W={'table_11_hyperparameters':[1.5,.6,.4,1.5],'table_08_literature':[1.1,1,.9,1,1,.8,1],
   'table_09_rat_physical':None,'table_07_why_marope_wins':[1.9,.7,1.2,1.2],'table_10_dual_utility':[1,1.2,1.2,1.2]}
AL={'l':r'\raggedright','r':r'\raggedleft','c':r'\centering'}
for p in sorted(glob.glob('tables/table_*.tex')):
    name=p.split('/')[-1][:-4]; s=open(p).read()
    if 'tabularx' in s: continue
    m=re.search(r'\\begin\{tabular\}\{([^}]*)\}',s); spec=m.group(1); n=len(spec)
    w=W.get(name) or [1.6]+[1]*(n-1)
    k=n/sum(w); w=[x*k for x in w]
    cols=''.join('>{\\hsize=%.3f\\hsize%s\\arraybackslash}X'%(wi,AL[c]) for wi,c in zip(w,spec))
    width='\\textwidth' if '\\begin{table*}' in s else '\\columnwidth'
    s=s.replace(m.group(0),'\\begin{tabularx}{%s}{%s}'%(width,cols)).replace('\\end{tabular}','\\end{tabularx}')
    open(p,'w').write(s)
