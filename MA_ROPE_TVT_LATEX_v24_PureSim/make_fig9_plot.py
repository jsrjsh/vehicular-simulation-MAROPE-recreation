"""Plot the regenerated queue-contention figure from results_fig9/*.json (see make_fig9_data.py). Also prints the numbers used in the text."""
import glob, json, os
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','STIXGeneral','DejaVu Serif'],'mathtext.fontset':'stix','font.size':8,
  'axes.labelsize':8.5,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7,'axes.linewidth':0.6,'axes.grid':True,'grid.color':'#d9d9d9',
  'grid.linewidth':0.4,'axes.axisbelow':True,'savefig.bbox':'tight','savefig.pad_inches':0.03,'pdf.fonttype':42})
HERE=os.path.dirname(os.path.abspath(__file__))
R=[json.load(open(f)) for f in glob.glob(os.path.join(HERE,'results_fig9','k*_seed*.json'))]
ks=sorted({r['k'] for r in R}); keys=['alloffload_queue_off','alloffload_queue_on','nooffload','maprope']
M={q:np.array([[r[q] for r in R if r['k']==k] for k in ks],dtype=object) for q in keys}
mean={q:np.array([np.mean(M[q][i]) for i in range(len(ks))]) for q in keys}; std={q:np.array([np.std(M[q][i],ddof=1) for i in range(len(ks))]) for q in keys}
print('seeds per k:',[len(M['maprope'][i]) for i in range(len(ks))])
for q in keys: print(f'{q:22s}',' '.join(f'{m:.3f}' for m in mean[q]))
sty={'alloffload_queue_off':('AllOffload, queue model OFF (flat)','#E69F00','--','x'),'alloffload_queue_on':('AllOffload, queue model ON (falling)','#D55E00','-','D'),
     'nooffload':('NoOffload (local)','#555555','-','s'),'maprope':('MA-ROPE (learned)','#0072B2','-','o')}
fig,ax=plt.subplots(figsize=(3.45,2.55))
for q in ('alloffload_queue_off','alloffload_queue_on','nooffload','maprope'):
    lab,c,ls,mk=sty[q]; ax.plot(ks,mean[q],color=c,ls=ls,marker=mk,ms=3.6,lw=1.3,label=lab)
    if q=='maprope': ax.fill_between(ks,mean[q]-std[q],mean[q]+std[q],color=c,alpha=0.18,lw=0)
for q,dy in (('alloffload_queue_off',0.012),('alloffload_queue_on',0.016)):
    ax.annotate({'alloffload_queue_off':'no queue','alloffload_queue_on':'shared queue'}[q],(ks[-1],mean[q][-1]),xytext=(ks[-1]-0.15,mean[q][-1]+dy),ha='right',fontsize=6.5,color=sty[q][1])
ax.set_xlabel('Vehicles sharing one RSU'); ax.set_ylabel('Utility $U_{PRR}$'); ax.set_xticks(ks)
h,l=ax.get_legend_handles_labels(); fig.legend(h,l,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(0.5,-0.14),columnspacing=1.0,handlelength=1.7)
fig.tight_layout(rect=(0,0.13,1,1)); fig.savefig(os.path.join(HERE,'figures','plots','fig_queue_contention.pdf'))
json.dump({'ks':ks,**{q:{'mean':mean[q].tolist(),'std':std[q].tolist()} for q in keys}},open(os.path.join(HERE,'results_fig9','summary.json'),'w'),indent=1)
