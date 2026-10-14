"""Redraw Figs 5-9 as vector PDFs from the CSVs that the original raster images were drawn from.
Data: results/speed_sweep_corrected/speed_sweep_results.csv  (Figs 5,6)
      results/CAMPAIGN_CORRECTED_20260803/CORRECTED_BASELINE_RESULTS.csv (Figs 7,8,9)
Values are unchanged from the original figures; only style/resolution differ. Error bars = std over 5 seeds."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R='../results/'
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','STIXGeneral','DejaVu Serif'],'mathtext.fontset':'stix',
  'font.size':8,'axes.labelsize':8.5,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7,'axes.linewidth':0.6,
  'lines.linewidth':1.3,'lines.markersize':4,'axes.grid':True,'grid.color':'#d9d9d9','grid.linewidth':0.4,'axes.axisbelow':True,
  'savefig.bbox':'tight','savefig.pad_inches':0.03,'pdf.fonttype':42})
ST={'ma-rope':('MA-ROPE (ours)','#0072B2','o','-'),'alloffload':('AllOffload','#D55E00','D','-'),'nooffload':('NoOffload','#555555','s','--'),
    'ucb_bandit':('UCB-RAT (recon.)','#E69F00','^','-'),'coopec_greedy':('CoopEC-RAT (recon.)','#009E73','v','-')}
COL,WIDE=3.45,7.16
def line(ax,x,g,m,err=True):
    lab,c,mk,ls=ST[m]; mean=g.mean(); sd=g.std()
    (ax.errorbar if err else ax.plot)(x,mean.values,**({'yerr':sd.values,'capsize':1.8,'elinewidth':0.7} if err else {}),color=c,marker=mk,ls=ls,label=lab,mfc=c,mec='white' if m=='ma-rope' else c,mew=0.4)
def tidy(ax,xl,yl): ax.set_xlabel(xl); ax.set_ylabel(yl)
# ---- speed sweep (Figs 5,6)
s=pd.read_csv(R+'speed_sweep_corrected/speed_sweep_results.csv'); sp=sorted(s.speed_kmh.unique())
def sg(m,col): return s[s.method==m].pivot(index='seed',columns='speed_kmh',values=col)
fig,ax=plt.subplots(1,2,figsize=(WIDE,2.35))
for m in ('ma-rope','alloffload','nooffload'):
    line(ax[0],sp,sg(m,'u_otr_active'),m,err=False); line(ax[1],sp,sg(m,'latency_active_ms'),m)
tidy(ax[0],'Vehicle speed (km/h)','$U_{OTR}$ (active tasks)'); tidy(ax[1],'Vehicle speed (km/h)','Average latency (ms)')
ax[0].set_title('(a)',loc='left',fontsize=8,fontweight='bold'); ax[1].set_title('(b)',loc='left',fontsize=8,fontweight='bold')
h,l=ax[0].get_legend_handles_labels(); fig.legend(h,l,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(0.5,-0.08))
fig.tight_layout(rect=(0,0.06,1,1)); fig.savefig('figures/plots/fig5_speed_utility_latency.pdf'); plt.close()
fig,ax=plt.subplots(figsize=(COL,2.3))
for m in ('ma-rope','alloffload','nooffload'): line(ax,sp,sg(m,'prr'),m)
tidy(ax,'Vehicle speed (km/h)','Empirical PRR'); ax.set_ylim(0.85,1.01); ax.legend(loc='lower left',frameon=True,framealpha=0.9,edgecolor='#cccccc',ncol=3,columnspacing=0.8,handlelength=1.6)
fig.tight_layout(); fig.savefig('figures/plots/fig6_prr_speed.pdf'); plt.close()
# ---- fleet sweep (Figs 7,8,9)
f=pd.read_csv(R+'CAMPAIGN_CORRECTED_20260803/CORRECTED_BASELINE_RESULTS.csv'); N=[8,16,32]
def fg(m,col,k=1): return (f[f.method==m].pivot(index='seed',columns='n_agents',values=col)*k)
fig,ax=plt.subplots(1,2,figsize=(COL,2.2))
for m in ('ma-rope','alloffload'):
    line(ax[0],N,fg(m,'conditional_tx_failure_rate',100),m); line(ax[1],N,fg(m,'fleet_tx_failure_rate',100),m)
for a,t,yl in ((ax[0],'(a)','Per-attempt failure (%)'),(ax[1],'(b)','Fleet-wide failure (%)')):
    tidy(a,'Fleet size $N$',yl); a.set_xticks(N); a.set_title(t,loc='left',fontsize=8,fontweight='bold'); a.set_xlim(5,35)
ax[0].set_ylim(0,8); ax[1].set_ylim(0,3.6)
h,l=ax[0].get_legend_handles_labels(); fig.legend(h,l,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(0.5,-0.07))
fig.tight_layout(rect=(0,0.06,1,1)); fig.savefig('figures/plots/fig7_link_failure.pdf'); plt.close()
order=('ma-rope','alloffload','nooffload','ucb_bandit','coopec_greedy')
for col,yl,out,ylim,loc in (('u_otr_active','$U_{OTR}$ (active tasks)','fig8_utility_fleet.pdf',(0.08,0.72),'upper right'),('fleet_otr','Fleet OTR','fig9_fleet_otr.pdf',(0,1.05),'lower left')):
    fig,ax=plt.subplots(figsize=(COL,2.5))
    for m in order: line(ax,N,fg(m,col),m,err=False)
    tidy(ax,'Fleet size $N$ (vehicles)',yl); ax.set_xticks(N); ax.set_xlim(6,34); ax.set_ylim(*ylim)
    h,l=ax.get_legend_handles_labels(); fig.legend(h,l,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(0.5,-0.02),columnspacing=1.0,handlelength=1.6)
    fig.tight_layout(rect=(0,0.16,1,1)); fig.savefig('figures/plots/'+out); plt.close()
# ---- Fig 2: contribution waterfall. Values are the labels printed on the original figure (0.8166 + 0.0084 + 0.0100 + 0.0050 + 0.0043 = 0.8443).
steps=[('+Queue\nawareness',0.0084),('+Multi-RAT\nselection',0.0100),('+DRL\npolicy vs\ngreedy',0.0050),('+FedAvg\ncoop.',0.0043)]
base=0.8166; fig,ax=plt.subplots(figsize=(COL,2.3)); ax.grid(axis='x',visible=False)
ax.bar(0,base-0.805,bottom=0.805,color='#A93232',width=0.6); ax.text(0,base+0.0012,f'{base:.4f}',ha='center',fontsize=7)
cur=base
for i,(l,d) in enumerate(steps,1):
    ax.bar(i,d,bottom=cur,color='#1B9E77',width=0.6); ax.text(i,cur+d+0.0012,f'+{d:.4f}',ha='center',fontsize=7,color='#0b5e45')
    ax.plot([i-0.7,i-0.3],[cur,cur],color='gray',lw=0.6,ls='--'); cur+=d
ax.bar(5,cur-0.805,bottom=0.805,color='#1F5FA6',width=0.6); ax.text(5,cur+0.0012,f'{cur:.4f}',ha='center',fontsize=7)
ax.plot([4.3,4.7],[cur,cur],color='gray',lw=0.6,ls='--')
ax.set_xticks(range(6)); ax.set_xticklabels(['AllOffload\n(baseline)']+[s[0] for s in steps]+['MA-ROPE\n(full)'],fontsize=7)
ax.set_ylim(0.805,0.8515); ax.set_ylabel('System utility (URLLC, $N{=}8$)'); ax.spines[['top','right']].set_visible(False)
fig.tight_layout(); fig.savefig('figures/plots/fig2_waterfall.pdf'); plt.close()
print('ok')
