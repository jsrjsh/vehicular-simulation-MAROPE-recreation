# agents/d3qn/replay.py
"""
Replay buffer implementation for uniform transition sampling in D3QN.
"""

import numpy as np
import torch
from collections import deque

class ReplayBuffer:
    """
    Standard experience replay buffer storing state transitions.
    Samples experiences uniformly.
    """
    def __init__(self, capacity: int = 10000, seed: int = None):
        self.buffer = deque(maxlen=capacity)
        self.rng = np.random.RandomState(seed)

    def add(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """Adds a transition to the replay buffer."""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> tuple:
        """Uniformly samples a batch of transitions."""
        indices = self.rng.choice(len(self.buffer), batch_size, replace=False)
        
        states, actions, rewards, next_states, dones = [], [], [], [], []
        for idx in indices:
            s, a, r, ns, d = self.buffer[idx]
            states.append(s)
            actions.append(a)
            rewards.append(r)
            next_states.append(ns)
            dones.append(d)
            
        # Convert list structures to PyTorch tensors
        states_t = torch.tensor(np.array(states), dtype=torch.float32)
        actions_t = torch.tensor(actions, dtype=torch.long)
        rewards_t = torch.tensor(rewards, dtype=torch.float32)
        next_states_t = torch.tensor(np.array(next_states), dtype=torch.float32)
        dones_t = torch.tensor(dones, dtype=torch.float32)
        
        return states_t, actions_t, rewards_t, next_states_t, dones_t

    def __len__(self) -> int:
        return len(self.buffer)
