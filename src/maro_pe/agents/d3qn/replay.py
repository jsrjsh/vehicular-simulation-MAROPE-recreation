# agents/d3qn/replay.py
"""
Configurable experience replay buffer for uniform and prioritized sampling.
Implements importance sampling weight corrections and beta annealing.
"""

import numpy as np
import torch

class ReplayBuffer:
    """
    Experience Replay Buffer supporting uniform and prioritized experience replay.
    Implemented as a ring-buffer to guarantee strict alignment between transitions
    and their sample priorities.
    """
    def __init__(self,
                 capacity: int = 10000,
                 mode: str = "uniform",
                 alpha: float = 0.6,
                 beta_start: float = 0.4,
                 beta_end: float = 1.0,
                 beta_anneal_steps: int = 50000,
                 epsilon: float = 1e-6,
                 seed: int = None):
        
        self.capacity = capacity
        if mode not in ["uniform", "prioritized"]:
            raise ValueError(f"Unknown replay mode: {mode}")
        self.mode = mode
        
        self.alpha = alpha
        self.beta = beta_start
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.beta_anneal_steps = beta_anneal_steps
        self.epsilon = epsilon
        
        self.rng = np.random.RandomState(seed)
        
        # Ring-buffer storage
        self.buffer = []
        self.pos = 0
        
        # Priority array
        self.priorities = np.zeros(capacity, dtype=np.float32)
        self.sample_step = 0

    def add(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """Adds a transition to the replay buffer, assigning max priority if prioritized."""
        transition = (state, action, reward, next_state, done)
        
        # Max priority calculation
        max_p = self.priorities[:len(self.buffer)].max() if len(self.buffer) > 0 else 1.0
        
        if len(self.buffer) < self.capacity:
            self.buffer.append(transition)
            self.priorities[len(self.buffer) - 1] = max_p
        else:
            self.buffer[self.pos] = transition
            self.priorities[self.pos] = max_p
        self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size: int) -> tuple:
        """
        Samples a batch of transitions.
        Returns: (states_t, actions_t, rewards_t, next_states_t, dones_t, indices, weights_t)
        """
        n = len(self.buffer)
        
        if self.mode == "uniform":
            indices = self.rng.choice(n, batch_size, replace=False)
            weights = np.ones(batch_size, dtype=np.float32)
        else:
            # Prioritized sampling
            self.sample_step += 1
            # Linear beta annealing: beta = beta_start + step * (beta_end - beta_start) / anneal_steps
            self.beta = min(self.beta_end, self.beta_start + self.sample_step * (self.beta_end - self.beta_start) / self.beta_anneal_steps)
            
            p = self.priorities[:n]
            # Probabilities P(i) = p_i^alpha / sum(p_k^alpha)
            p_alpha = p ** self.alpha
            probs = p_alpha / p_alpha.sum()
            
            indices = self.rng.choice(n, batch_size, replace=False, p=probs)
            
            # Importance sampling weights w_i = (N * P(i))^(-beta)
            weights = (n * probs[indices]) ** (-self.beta)
            # Normalize by max weight
            weights /= weights.max()
            weights = weights.astype(np.float32)
            
        states, actions, rewards, next_states, dones = [], [], [], [], []
        for idx in indices:
            s, a, r, ns, d = self.buffer[idx]
            states.append(s)
            actions.append(a)
            rewards.append(r)
            next_states.append(ns)
            dones.append(d)
            
        states_t = torch.tensor(np.array(states), dtype=torch.float32)
        actions_t = torch.tensor(actions, dtype=torch.long)
        rewards_t = torch.tensor(rewards, dtype=torch.float32)
        next_states_t = torch.tensor(np.array(next_states), dtype=torch.float32)
        dones_t = torch.tensor(dones, dtype=torch.float32)
        weights_t = torch.tensor(weights, dtype=torch.float32)
        
        return states_t, actions_t, rewards_t, next_states_t, dones_t, indices, weights_t

    def update_priorities(self, indices: np.ndarray, td_errors: np.ndarray):
        """Updates transition priorities based on absolute TD errors."""
        if self.mode == "prioritized":
            # p_i = |TD_error| + epsilon
            self.priorities[indices] = np.abs(td_errors) + self.epsilon

    def __len__(self) -> int:
        return len(self.buffer)
