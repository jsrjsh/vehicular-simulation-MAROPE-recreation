content = r"""
\section{System Model and Problem Formulation}

\subsection{Network Architecture}

We consider a two-tier V2X network comprising N vehicles, R roadside units (RSUs) each co-located with a MEC server, and a base station (BS) providing wide-area LTE and 5G-NR coverage. Each vehicle has an on-board ECU (2-5 TOPS) and a multi-RAT module supporting LTE, ITS-G5, WiFi-6, and 5G-NR simultaneously. \Cref{fig:architecture} illustrates the system architecture.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.45\textwidth]{example-image-a}
\caption{MA-ROPE System Architecture---two-tier V2X with 4-RAT heterogeneous access and FedAvg coordination.}
\label{fig:architecture}
\end{figure}

\subsection{RAT Physical Layer Model}

Following Yacheur et al. \cite{9} \Cref{tab:rat_physical}, we assign per-RAT physical parameters as in \Cref{tab:rat_physical}. LTE and 5G-NR operate at -110 dBm noise floor; ITS-G5 and WiFi-6 at -90 dBm. Cellular RATs experience Jakes Doppler fading at vehicular speeds; ITS-G5 and WiFi-6 use the Constant Speed propagation model, as analyzed in Fig. 14.

\begin{table}[htbp]
\caption{RAT Physical Parameters (Yacheur 2023 + 3GPP Standards)}
\label{tab:rat_physical}
\centering
\resizebox{\columnwidth}{!}{%
\begin{tabular}{|l|c|c|c|c|c|c|}
\hline
\textbf{RAT} & \textbf{Delay} & \textbf{Throughput} & \textbf{Noise Floor} & \textbf{Fading} & \textbf{Path Loss} & \textbf{Source} \\
\hline
LTE & 20 ms & 50 Mbps & -110 dBm & Jakes & TR 36.885 & \cite{9} \\
ITS-G5 & 10 ms & 27 Mbps & -90 dBm & Constant & TR 36.885 & \cite{9} \\
WiFi-6 & 5 ms & 600 Mbps & -90 dBm & Constant & 802.11ax & \cite{12} \\
5G-NR & 1 ms & 1 Gbps & -110 dBm & Jakes & TR 38.901 & \cite{13} \\
\hline
\end{tabular}%
}
\end{table}

The SINR for RAT $r$ at distance $d$ with vehicle speed $v$ governs per-PDU delivery probability:

\begin{equation}
\label{eq:sinr}
\text{SINR}_r(d,v) = P_{tx} - \text{PL}_r(d) - N_r - Sh_r - F_r(v)
\end{equation}

where $\text{PL}_r(d)$ is RAT-specific path loss, $N_r$ is noise floor, $Sh_r \sim \mathcal{N}(0,\sigma^2_r)$ is shadowing, and $F_r(v)$ is Jakes fading loss. SINR drives a per-PDU Bernoulli draw with $p_{link} = \sigma(\text{SINR}_r - \theta_r)$ but is NOT the reported PRR metric. Packet Reception Ratio is defined empirically from actual packet counters:

\begin{equation}
\label{eq:prr}
\text{PRR} = \frac{n_{rx}}{n_{tx}}
\end{equation}

where $n_{tx}$ is the number of offload PDU transmission attempts and $n_{rx}$ is PDUs successfully delivered. This separates the physical link model from the reported metric: PRR reflects real packet outcomes, not a smoothed SINR function. Per-RAT empirical PRR fills observation slots obs[4:8]; slots default to 0.5 (unknown) before any attempt on that RAT. The raw link delivery probability $p_{link}$ is separately tracked in infos["link\_delivery\_prob"] for PHY-curve versus measured-PRR comparison.

\subsection{Task Model}

Each vehicle generates task $\tau_i = (C_i, D_i, L_i, T_i)$ where $C_i$ is computational workload (CPU cycles), $D_i$ is data volume (MB), $L_i$ is maximum tolerable delay (ms), and $T_i \in \{\text{safety}, \text{infotainment}, \text{compute}\}$ determines deadline: safety tasks require $L_i = 100$ ms (SAE J3016 Level 4), infotainment 500 ms, compute 2000 ms.

\subsection{End-to-End Latency Model}

End-to-end task latency is the primary measurable QoS quantity in this work. For each offload PDU attempt at step t, the total latency decomposes into four additive components:

\begin{subequations}
\label{eq:latency_all}
\begin{equation}
\label{eq:ltotal_base}
L_{total} = L_{prop} + L_{tx} + L_{remote} + L_{queue}
\end{equation}

where $L_{prop} = d/(2c/3)$ is propagation delay over vehicle-to-RSU distance d at 2/3 speed of light; $L_{tx} = D_i/\text{BW}_r$ is transmission delay for data volume $D_i$ (MB) over RAT bandwidth $\text{BW}_r$; $L_{remote} = C_i/f_{MEC}$ is remote compute delay for workload $C_i$ (CPU cycles) at MEC frequency $f_{MEC}$; and $L_{queue} = 1/(\mu_k - \lambda_k)$ is the M/M/1 queuing delay at the shared RSU, where $\mu_k$ is the server service rate and $\lambda_k$ is the total vehicle arrival rate across all co-located vehicles. The $L_{queue}$ term is the critical shared-resource term --- it couples all vehicles' decisions through the common RSU queue and is responsible for the AllOffload collapse observed in Section V.

For partial offloading with ratio $\rho$, local and remote execution proceed in parallel following the model of Mao et al. \cite{14}. The realized end-to-end delay is:

\begin{equation}
\label{eq:ltotal_partial}
L_{total} = L_{prop} + \rho \cdot L_{tx} + \max(\rho \cdot L_{remote}, (1-\rho) \cdot L_{local}) + L_{queue}
\end{equation}

where $\rho \in \{0.25, 0.50, 0.75, 1.0\}$ is the partial offload ratio, $\rho \cdot L_{tx}$ captures the transmitted data fraction, and $L_{local} = C_i/f_{ECU}$ is local ECU compute time. When $\rho = 0$ (pure local execution), $L_{total} = L_{local}$ and no PDU is transmitted over the radio; such steps are excluded from latency QoS accounting since no V2X packet is at risk.

\textbf{Deadline classification.} Each offload PDU outcome is classified into one of three measurable QoS categories relative to the task-type deadline $D_i$: (1) \textit{delivered\_on\_time}: link success AND $L_{total} \leq D_i$ --- a useful delivery; (2) \textit{delivered\_late}: link success AND $L_{total} > D_i$ --- received but stale, wasted transmission; (3) \textit{not\_delivered}: link failure (Bernoulli draw on $p_{link}$) --- channel loss. The on-time delivery rate is:

\begin{equation}
\label{eq:otr}
\text{OTR} = \frac{n_{rx\_on\_time}}{n_{tx}}
\end{equation}
\end{subequations}

Note that $\text{OTR} \leq \text{PRR}$ always, since PRR counts all link-successful receptions regardless of deadline. The gap ($\text{PRR} - \text{OTR}$) is the latency-induced deadline violation rate --- packets the channel delivered, but the application could not use. This is the quantity MA-ROPE directly minimises via the $\exp(-L/D)$ term in the utility reward (\Cref{eq:utility_all}).

\subsection{Energy and Utility}

Total energy consumption is $E_{total} = P_{tx} \cdot L_{tx} + \epsilon_r \cdot \rho \cdot D_i$, where $P_{tx} \cdot L_{tx}$ captures radio transmit energy over the realized transmission duration and $\epsilon_r$ (J/MB) is the RAT-specific processing or transfer energy cost. MA-ROPE defines two complementary utility functions, each optimized for a different deployment criterion (Yacheur et al. \cite{9} Eq. (2) extended):

\begin{subequations}
\label{eq:utility_all}
\begin{align}
U_{PRR} &= \alpha \cdot \text{PRR} + \frac{\beta}{Z} \left[ \frac{1}{2}\exp\left(-\frac{L}{D}\right) + \frac{1}{2}\exp\left(-\frac{E}{3}\right) + \frac{1}{4}\Delta\text{CBR} \right] \label{eq:uprr} \\
U_{OTR} &= \alpha \cdot \text{OTR} + \frac{\beta}{Z} \left[ \frac{1}{2}\exp\left(-\frac{L}{D}\right) + \frac{1}{2}\exp\left(-\frac{E}{3}\right) + \frac{1}{4}\Delta\text{CBR} \right] \label{eq:uotr} \\
Z &= 1.25 \label{eq:z}
\end{align}
\end{subequations}

$U_{PRR}$ (\Cref{eq:uprr}) uses empirical $\text{PRR} = n_{rx}/n_{tx}$ as the reliability term and provides dense reward feedback during DQN training. $U_{OTR}$ (\Cref{eq:uotr}) replaces PRR with $\text{OTR} = n_{rx\_on\_time}/n_{tx}$, the fraction of PDUs delivered within deadline, and is the primary deployment criterion for safety-critical SAE J3016 workloads. The normalization constant Z makes the auxiliary latency, energy, and CBR block sum to $\beta$; $\alpha + \beta = 1$. Task-adaptive weights are grounded in the task-mix prior: safety $\alpha=0.70$, infotainment $\alpha=0.40$, and compute $\alpha=0.20$. The $\Delta\text{CBR}$ term remains an early-warning congestion signal orthogonal to the explicit queue model.

\begin{table}[htbp]
\caption{Dual Utility Criteria in MA-ROPE (\Cref{eq:uprr} and \Cref{eq:uotr})}
\label{tab:dual_utility}
\centering
\resizebox{\columnwidth}{!}{%
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Criterion} & \textbf{Reliability Term} & \textbf{Training Use} & \textbf{Deployment Use} \\
\hline
$U_{PRR}$ (\Cref{eq:uprr}) & $\text{PRR} = n_{rx}/n_{tx}$ & DQN training signal (dense reward) & Throughput / balanced scenarios \\
$U_{OTR}$ (\Cref{eq:uotr}) & $\text{OTR} = n_{rx\_on\_time}/n_{tx}$ & Evaluation metric (not used in DQN training) & Safety V2X (SAE J3016 Level 4) \\
\hline
\end{tabular}%
}
\end{table}
"""
with open('MA_ROPE_TVT_LATEX/sections/system_model.tex', 'w') as f:
    f.write(content.strip())

