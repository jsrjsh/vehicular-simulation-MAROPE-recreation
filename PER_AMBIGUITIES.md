# PER_AMBIGUITIES.md

This document lists all ambiguities identified during the implementation of Prioritized Experience Replay (PER) and documents our technical resolutions.

---

## Identified Ambiguities

### Ambiguity 1: Value of Priority Epsilon ($\epsilon_p$)
* **Description:** The Recreation Guide states that a small positive constant $\epsilon_p$ is added to absolute TD errors to prevent transitions from having zero sampling probability, but does not provide a value.
* **Resolution:** We adopted the standard value of **$1\text{e-}6$** (as used in the original PER paper by Schaul et al.).
* **Physical / Computational Rationale:** Too small of an epsilon (e.g. $1\text{e-}15$) leads to underflows in float32 arithmetic, while too large of an epsilon (e.g. $1\text{e-}1$) overrides the TD-error priority, rendering prioritization ineffective. $1\text{e-}6$ is the stable benchmark.

### Ambiguity 2: Beta Annealing Profile Shape
* **Description:** The guide defines $\beta: 0.4 \to 1.0$ over 50,000 steps, but does not specify the trajectory (linear, exponential, or cosine).
* **Resolution:** We implemented a **linear annealing** schedule:
  $$\beta_t = \min\left(1.0, 0.4 + t \cdot \frac{0.6}{50000}\right)$$
* **Physical / Computational Rationale:** Linear annealing of the importance sampling exponent is standard, safe, and guarantees that importance weights slowly scale up to full correction ($\beta=1.0$) linearly, stabilizing early training gradients.

### Ambiguity 3: Initial Priority for New Experiences
* **Description:** The guide does not define what priority should be given to newly inserted transitions.
* **Resolution:** We assign the **maximum priority** currently present in the buffer (defaulting to $1.0$ if empty).
* **Physical / Computational Rationale:** This guarantees that every transition is sampled at least once before its priority is adjusted by its actual TD-error. Without this, new experiences could be permanently starved of training iterations if they are initialized with zero or low default priority.

### Ambiguity 4: Step Counter for Annealing
* **Description:** It is not specified whether the 50,000 steps for $\beta$ annealing refer to environment steps or gradient descent updates.
* **Resolution:** We increment the annealing steps on **every learning step (gradient update)**.
* **Physical / Computational Rationale:** This ties importance weight corrections directly to the active optimization updates, ensuring that full correction ($\beta = 1.0$) is reached when the networks have undergone 50,000 weights adjustments.
