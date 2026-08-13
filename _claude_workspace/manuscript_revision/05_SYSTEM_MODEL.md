# System Model Section (Revision Draft v1)

Factual description of the implemented environment (`env/config.py`, `env/channel.py`,
`env/environment.py`). No design decisions here — this documents what the code does.

### 4.1 Network and radio access technologies

Each vehicle chooses among five link options at every decision step: compute locally, or offload
via one of four heterogeneous RATs — LTE, ITS-G5, 5G-NR, or WiFi-6. Each RAT is parameterized by
carrier frequency, transmit power, noise floor, shadow-fading standard deviation, an SINR
detection threshold, a path-loss model (3GPP V2X for LTE/ITS-G5, 5G UMi for 5G-NR, WiFi-ax for
WiFi-6), and a nominal throughput (LTE 50 Mbps, ITS-G5 27 Mbps, WiFi-6 600 Mbps, 5G-NR 1000 Mbps).
LTE and 5G-NR additionally model Jakes/Rayleigh fading as a function of vehicle speed; ITS-G5 and
WiFi-6 use a constant-fading approximation.

### 4.2 Channel model

Instantaneous SINR is computed per link as transmit power minus path loss minus noise floor, plus
a zero-mean Gaussian shadow-fading sample, minus any Jakes fading loss. Link success is drawn as a
Bernoulli trial with a sigmoid probability centered on the RAT's SINR threshold (steepness scaled
by the shadow-fading standard deviation), rather than a hard threshold — a link close to its
threshold can succeed or fail probabilistically, which is what makes the offload-ratio decision
meaningful rather than trivial. This is a deterministic-parameter, stochastically-sampled
analytical channel model (Shannon-Hartley-based), not a full network-layer simulation; see
Limitations 7.1 for the precise scope of what this does and does not capture.

### 4.3 Action space

Eleven discrete actions, each a (RAT, offload-ratio) pair: local-only; LTE at 25/50/75%; ITS-G5 at
25/50%; 5G-NR at 25/50/100%; WiFi-6 at 50/100%. The offload ratio is the fraction of a task's
compute offloaded to the network target rather than executed locally — a continuous-valued lever
discretized into policy-relevant levels, not a binary offload/no-offload choice. Safety-class tasks
have LTE actions masked out (both during action selection and during the Double-DQN target
computation), reflecting a latency-critical/reliability constraint specific to that task class.

### 4.4 Task model

Three task types — safety (100ms deadline, 0.1MB, latency-weighted reward), infotainment (500ms
deadline, 2MB, balanced reward), and compute (1000ms deadline, 5MB, throughput-weighted reward) —
each with its own deadline, payload size, CPU-cycle requirement, and reward weighting (alpha for
latency, beta for throughput/energy) reflecting the different tolerance each task class has for
delay versus resource cost. Task-type mix is scenario-dependent (a URLLC-heavy mix, a balanced mix,
and a compute-heavy mix are all defined), letting the evaluated environment span a range of
workload characters rather than a single fixed mix.

### 4.5 Utility functions and fleet-level metrics

Two active-task utility functions are tracked per policy: U_PRR (packet/task reception reliability)
and U_OTR (on-time completion rate under the task's deadline). Beyond the active-task metrics, this
revision reports fleet-wide statistics computed over *all* generated tasks, not only attempted
transmissions — Fleet OTR, fleet-wide transmission failure rate, and absolute failure counts — a
distinction that is central to Section 5.2's reliability decomposition and is a deliberate design
choice of this revision's reporting, not an artifact of the simulator itself.

### 4.6 Fleet density and RSU queuing

Vehicles are distributed along a defined road segment served by a small number of fixed RSU
positions; an optional RSU queue models per-RSU compute/transmission backlog, contributing an
additional latency term proportional to queue depth. Fleet density (vehicle count) is varied
across N=8/16/32 in this evaluation to test how each policy's reliability degrades under rising
contention for shared RSU and channel resources.
