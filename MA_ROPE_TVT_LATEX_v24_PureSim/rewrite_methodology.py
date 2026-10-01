import re

with open('sections/methodology.tex', 'r') as f:
    content = f.read()

# I will just write a python script to do simple string replacements for the itemize blocks.
# Block 1: Task and Transmission Model
b1_old = """Each task is characterized by:
\\begin{itemize}
  \\item Computational complexity: $C_{\\text{task}} \\in \\{C_{\\min}, C_{\\min} + \\Delta C, \\ldots, C_{\\max}\\}$ (CPU cycles)
  \\item Transmission size: $B_{\\text{task}}$ (bits), determined by task type
  \\item Deadline: $D_{\\text{max}}$ (milliseconds), task-dependent
  \\item Arrival time: $t_{\\text{arrival}}$
\\end{itemize}"""
b1_new = """Each task is characterized by its computational complexity ($C_{\\text{task}}$ in CPU cycles, ranging from $C_{\\min}$ to $C_{\\max}$ in steps of $\\Delta C$), transmission size ($B_{\\text{task}}$ in bits, determined by task type), application deadline ($D_{\\text{max}}$ in milliseconds, which is task-dependent), and its arrival time $t_{\\text{arrival}}$."""

content = content.replace(b1_old, b1_new)

# Block 2: State Space Definition
b2_old = """where:
\\begin{itemize}
  \\item $n_m(t) \\in \\{1, 2, \\ldots, N_{\\text{max}}\\}$: Number of vehicles on RAT $m$ (LTE, ITS-G5, WiFi-6, 5G-NR) during window \\Delta t = 1$ second
  \\item $q(t) \\in \\{0, 1, \\ldots, Q_{\\text{max}}\\}$: Current MEC server queue length (number of pending compute tasks)
  \\item $h_m(t) \\in \\{0, 1, \\ldots, H_{\\max}\\}$: Channel state index for RAT $m$ (Jakes fading quantized to $H_{\\max} = 8$ levels based on SNR thresholds)
  \\item Observation window: $\\Delta t = 1$ second (state updated every decision epoch)
  \\item State discretization: Density counts are integers; queue length is integer; channel states are discrete 8-level indices
\\end{itemize}"""

b2_old_2 = """where:
\\begin{itemize}
  \\item $n_m(t) \\in \\{1, 2, \\ldots, N_{\\text{max}}\\}$: Number of vehicles on RAT $m$ (LTE, ITS-G5, WiFi-6, 5G-NR) during window $\\Delta t = 1$ second
  \\item $q(t) \\in \\{0, 1, \\ldots, Q_{\\text{max}}\\}$: Current MEC server queue length (number of pending compute tasks)
  \\item $h_m(t) \\in \\{0, 1, \\ldots, H_{\\max}\\}$: Channel state index for RAT $m$ (Jakes fading quantized to $H_{\\max} = 8$ levels based on SNR thresholds)
  \\item Observation window: $\\Delta t = 1$ second (state updated every decision epoch)
  \\item State discretization: Density counts are integers; queue length is integer; channel states are discrete 8-level indices
\\end{itemize}"""

b2_new = """where $n_m(t) \\in \\{1, 2, \\ldots, N_{\\text{max}}\\}$ represents the number of vehicles on RAT $m$ (LTE, ITS-G5, WiFi-6, 5G-NR) during a $\\Delta t = 1$ second observation window, $q(t) \\in \\{0, 1, \\ldots, Q_{\\text{max}}\\}$ is the current MEC server queue length denoting pending compute tasks, and $h_m(t) \\in \\{0, 1, \\ldots, H_{\\max}\\}$ is the channel state index for RAT $m$, reflecting Jakes fading quantized to 8 levels based on SNR thresholds. The state is updated every decision epoch with density counts and queue lengths as integers, and channel states as discrete indices."""

content = content.replace(b2_old, b2_new).replace(b2_old_2, b2_new)


# Block 3: Action Space Definition
b3_old = """where:
\\begin{itemize}
  \\item $m_t \\in M = \\{\\text{LTE}, \\text{ITS-G5}, \\text{WiFi-6}, \\text{5G-NR}\\}$ (4 RAT options)
  \\item $\\rho_t \\in R = \\{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\\}$ (6 offload ratio levels)
  \\item Theoretical action space: $|A| = M \\times R = 4 \\text{ RATs} \\times 6 \\text{ }\\rho\\text{ values} = 24$ potential (RAT, $\\rho$) pairs
  \\item Implemented action space: $|A| = 11$ discrete actions, selected from the 24 potential pairs via strategic masking:
    \\begin{itemize}
      \\item Local execution ($\\rho=0$): 1 action
      \\item 5G-NR ($\\rho \\in \\{0.5, 0.75, 1.0\\}$): 3 actions --- reliable fallback RAT
      \\item WiFi-6 ($\\rho \\in \\{0.25, 0.5, 0.75\\}$): 3 actions --- high bandwidth, short range
      \\item ITS-G5 ($\\rho \\in \\{0.5, 0.75\\}$): 2 actions --- V2X-specialized
      \\item LTE ($\\rho \\in \\{0.75, 1.0\\}$): 2 actions --- wide coverage fallback
      \\item Total: $1 + 3 + 3 + 2 + 2 = 11$ actions
    \\end{itemize}
  \\item Rationale for 11-action subset: Certain RAT-$\\rho$ combinations are infeasible or suboptimal (e.g., LTE at $\\rho=0.25$ or $0.5$ is bandwidth-limited; ITS-G5 at $\\rho=1.0$ exceeds its range envelope). The 11-action set covers all strategically distinct decisions while avoiding these degenerate cases. Invalid actions are masked in the DQN $\\epsilon$-greedy exploration.
\\end{itemize}"""
b3_new = """where $m_t \\in M$ represents the 4 RAT options (LTE, ITS-G5, WiFi-6, 5G-NR) and $\\rho_t \\in R$ denotes the 6 offload ratio levels from 0.0 to 1.0. This defines a theoretical action space of $|A| = 24$ potential (RAT, $\\rho$) pairs. The implemented action space, however, consists of 11 discrete actions selected via strategic masking to avoid infeasible or suboptimal combinations (e.g., LTE at low offload ratios being bandwidth-limited, or ITS-G5 at full offloading exceeding its range envelope). These 11 actions include 1 action for local execution ($\\rho=0$), 3 actions for 5G-NR (reliable fallback), 3 for WiFi-6 (high bandwidth, short range), 2 for ITS-G5 (V2X-specialized), and 2 for LTE (wide coverage fallback). Invalid actions are masked in the DQN $\\epsilon$-greedy exploration."""

content = content.replace(b3_old, b3_new)

# Block 4: Reward Function
b4_old = """where:
\\begin{itemize}
  \\item $\\text{OTR}_t = \\frac{\\text{tasks completed on-time in epoch } t}{\\text{total tasks in epoch } t}$ (dimensionless, $\\in [0, 1]$)
  \\item $L_t$ = actual task completion latency (milliseconds), including transmission + queue wait + MEC processing
  \\item $D_{\\max} = 100$ ms (URLLC deadline threshold, tuned per scenario)
  \\item $E_t$ = energy consumed by transmission in epoch $t$ (joules)
  \\item Weights: $w_1 = 0.6$, $w_2 = 0.3$, $w_3 = 0.1$ (normalized to unit sum; tuned via grid search in preliminary experiments)
  \\item Justification: OTR directly encodes deadline compliance (primary goal); latency penalty discourages marginally-late deliveries; energy penalty prevents wasteful transmission strategies
\\end{itemize}"""
b4_new = """where $\\text{OTR}_t$ is the dimensionless ratio of tasks completed on-time to total tasks in epoch $t$, $L_t$ is the actual task completion latency in milliseconds (including transmission, queue wait, and MEC processing), $D_{\\max}$ is the URLLC deadline threshold (e.g., 100 ms), and $E_t$ is the energy consumed by transmission in epoch $t$ in joules. The weights $w_1 = 0.6$, $w_2 = 0.3$, and $w_3 = 0.1$ are normalized to a unit sum and were tuned via grid search in preliminary experiments. This formulation directly encodes deadline compliance through OTR as the primary goal, discourages marginally-late deliveries via the latency penalty, and prevents wasteful transmission strategies using the energy penalty."""

content = content.replace(b4_old, b4_new)

# Subsections of D (Simulation Environment Specification)
b5_old = """\\subsubsection{Python Framework and Simulator}

\\begin{itemize}
  \\item \\textbf{Language:} Python 3.8+
  \\item \\textbf{Deep learning:} PyTorch 1.10.0 (GPU acceleration via CUDA 11.3)
  \\item \\textbf{MDP simulator:} Custom environment class (no external dependency on ns-3 or SUMO for the pure-simulation track)
  \\item \\textbf{Numerical libraries:} NumPy 1.21.0, SciPy 1.7.0
  \\item \\textbf{Logging and visualization:} Pandas, Matplotlib, TensorBoard
\\end{itemize}"""
b5_new = """\\subsubsection{Python Framework and Simulator}

The framework is implemented in Python 3.8+ utilizing PyTorch 1.10.0 with CUDA 11.3 for GPU-accelerated deep learning. The MDP simulator is a custom environment class designed without external dependencies on ns-3 or SUMO for the pure-simulation track. Numerical operations are handled by NumPy 1.21.0 and SciPy 1.7.0, while Pandas, Matplotlib, and TensorBoard are used for logging and visualization."""

content = content.replace(b5_old, b5_new)


b6_old = """\\subsubsection{Vehicle Mobility and Traffic Pattern}

\\begin{itemize}
  \\item \\textbf{Mobility model:} Synthetic Random Waypoint within a $10 \\text{ km} \\times 10 \\text{ km}$ grid
  \\item \\textbf{Vehicle speed:} Uniformly sampled from $\\{5, 10, 15, 20, 25, 30\\}$ m/s (urban to highway speeds)
  \\item \\textbf{Direction change frequency:} Every 30--60 seconds with random waypoint selection
  \\item \\textbf{Task arrival rate:} Poisson process with rate $\\lambda = 1$ task/vehicle/second (URLLC stress scenario)
  \\item \\textbf{Task size distribution:} Log-normal, mimicking real V2X compute workloads
\\end{itemize}"""
b6_new = """\\subsubsection{Vehicle Mobility and Traffic Pattern}

Vehicle mobility follows a Synthetic Random Waypoint model within a $10 \\text{ km} \\times 10 \\text{ km}$ grid. Vehicle speeds are uniformly sampled from 5 to 30 m/s to represent urban to highway conditions, with direction changes occurring every 30 to 60 seconds towards randomly selected waypoints. Task generation is modeled as a Poisson process with an arrival rate of $\\lambda = 1$ task per vehicle per second for the URLLC stress scenario, and task sizes follow a log-normal distribution to mimic real V2X compute workloads."""
content = content.replace(b6_old, b6_new)

b7_old = """\\subsubsection{MEC Server Queue Model}

\\begin{itemize}
  \\item \\textbf{Queue type:} FIFO (First-In-First-Out), shared among all $N$ vehicles
  \\item \\textbf{Processing capacity:} $\\mu = 1000$ tasks/second (capable edge server)
  \\item \\textbf{Service time per task:} $T_{\\text{service}} = \\frac{C_{\\text{remote}}}{\\text{MHz}}$, where CPU frequency is 2000 MHz
  \\item \\textbf{Maximum queue depth:} $Q_{\\max} = 100$ tasks (after which new submissions are dropped)
  \\item \\textbf{Queue length observation:} Vehicles observe queue length (discretized to 8 levels) every $\\Delta t = 1$ second
\\end{itemize}"""
b7_new = """\\subsubsection{MEC Server Queue Model}

The MEC server operates a First-In-First-Out (FIFO) queue shared among all $N$ vehicles. It has a processing capacity of $\\mu = 1000$ tasks per second, with service time per task calculated based on a remote CPU frequency of 2000 MHz. The maximum queue depth is limited to 100 tasks, beyond which new submissions are dropped. Vehicles observe this queue length, discretized to 8 levels, every 1-second interval."""
content = content.replace(b7_old, b7_new)


b8_old = """\\begin{itemize}
  \\item $T_{\\text{tx}} = \\frac{\\rho \\cdot B_{\\text{task}}}{\\text{datarate}(m_t, h_m(t))}$ (transmission time on selected RAT $m_t$ with channel state $h_m(t)$)
  \\item $T_{\\text{queue}} = \\frac{\\text{queue length at arrival}}{1000}$ (in seconds, given $\\mu = 1000$ tasks/s)
  \\item $T_{\\text{mec}} = \\frac{\\rho \\cdot C_{\\text{task}}}{2000}$ (in seconds, MEC processes at 2000 MHz)
  \\item $T_{\\text{local}} = \\frac{(1 - \\rho) \\cdot C_{\\text{task}}}{\\text{device CPU speed}}$ (parallel to transmission/MEC; device CPU = 1000 MHz)
  \\item Deadline compliance: Task $\\tau$ is on-time if $t_{\\text{arrive}} + L_{\\text{total}}(\\tau) \\le t_{\\text{arrive}} + D_{\\max}$

\\end{itemize}"""
b8_new = """Here, $T_{\\text{tx}}$ is the transmission time on the selected RAT $m_t$ given channel state $h_m(t)$, and $T_{\\text{queue}}$ is the wait time in seconds based on a 1000 tasks/s service rate. $T_{\\text{mec}}$ and $T_{\\text{local}}$ represent the execution times at the MEC server (processing at 2000 MHz) and the local device CPU (processing at 1000 MHz), respectively. A task $\\tau$ is considered compliant if its total latency plus arrival time does not exceed the task deadline $D_{\\max}$."""
content = content.replace(b8_old, b8_new)

b9_old = """\\subsubsection{Reproducibility Configuration}

\\begin{itemize}
  \\item \\textbf{Random seeds:} 5 independent random seeds (0, 1, 2, 3, 4) for all training and evaluation runs
  \\item \\textbf{Training episodes per run:} 100 episodes per vehicle (per density)
  \\item \\textbf{Evaluation window:} Final 5 episodes of training (after convergence)
  \\item \\textbf{Code repository:} [GitHub/GitLab URL to public submission repository]
  \\item \\textbf{Supplementary files:} Configuration YAML files, checkpoint weights, and raw evaluation logs are available in supplementary materials
\\end{itemize}"""
b9_new = """\\subsubsection{Reproducibility Configuration}

To ensure reproducibility, experiments utilize 5 independent random seeds for all training and evaluation runs. Each run comprises 100 training episodes per vehicle per density, with the evaluation window defined as the final 5 episodes post-convergence. The code repository, configuration YAML files, checkpoint weights, and raw evaluation logs are made available in the supplementary materials."""
content = content.replace(b9_old, b9_new)

# Standardize subsections
content = content.replace("\\subsubsection", "\\subsection")

with open('sections/methodology.tex', 'w') as f:
    f.write(content)
