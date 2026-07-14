# agents/d3qn/network.py
"""
Dueling neural network architecture for the MA-ROPE simulation platform.
Splits Q-value updates into State Value and Action Advantage streams.
"""

import torch
import torch.nn as nn

class DuelingQNetwork(nn.Module):
    """
    Dueling Q-Network for single-agent decision making.
    Input: 12-dimensional state vector.
    Output: 11 action advantage values recombined with state value.
    """
    def __init__(self, state_dim: int = 12, action_dim: int = 11):
        super(DuelingQNetwork, self).__init__()
        
        # Shared feature representation layers
        self.shared = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU()
        )
        
        # State value head V(s)
        self.value_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        
        # Action advantage head A(s, a)
        self.advantage_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass mapping state to Q-values.
        Q(s, a) = V(s) + A(s, a) - mean_a(A(s, a))
        """
        features = self.shared(state)
        values = self.value_head(features)
        advantages = self.advantage_head(features)
        
        # Recombine using the mean-deducted advantage formulation
        q_values = values + (advantages - advantages.mean(dim=-1, keepdim=True))
        return q_values
