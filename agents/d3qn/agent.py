# agents/d3qn/agent.py
"""
Dueling Double DQN Agent implementation for MA-ROPE.
Includes prioritized experience replay integration, epsilon-greedy decay,
Double-DQN target math, and safety task action masking.
"""

import os
import math
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from agents.d3qn.network import DuelingQNetwork
from agents.d3qn.replay import ReplayBuffer

class D3QNAgent:
    """
    Dueling Double DQN Agent.
    Interfaces with V2XEnv and implements uniform/prioritized experience replay,
    weighted Huber loss, hard target network updates, and safety policy action filters.
    """
    def __init__(self,
                 state_dim: int = 12,
                 action_dim: int = 11,
                 gamma: float = 0.95,
                 lr: float = 1e-3,
                 buffer_capacity: int = 10000,
                 batch_size: int = 32,
                 target_update_frequency: int = 100,
                 epsilon_start: float = 1.0,
                 epsilon_end: float = 0.05,
                 epsilon_decay_steps: int = 2000,
                 replay_mode: str = "uniform",
                 seed: int = None):
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_frequency = target_update_frequency
        
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay_steps = epsilon_decay_steps
        self.epsilon = epsilon_start
        
        self.rng = np.random.RandomState(seed)
        self.seed_val = seed
        
        # Replay Buffer
        self.replay_buffer = ReplayBuffer(
            capacity=buffer_capacity,
            mode=replay_mode,
            alpha=0.6,
            beta_start=0.4,
            beta_end=1.0,
            beta_anneal_steps=50000,
            epsilon=1e-6,
            seed=seed
        )
        
        # Networks
        self.online_net = DuelingQNetwork(state_dim, action_dim)
        self.target_net = DuelingQNetwork(state_dim, action_dim)
        
        # Hard copy online to target
        self.update_target_network()
        # Freeze target network
        for param in self.target_net.parameters():
            param.requires_grad = False
            
        # Optimizer and Loss
        self.optimizer = optim.Adam(self.online_net.parameters(), lr=lr)
        # SmoothL1Loss with no reductions to support importance weights
        self.loss_fn = nn.SmoothL1Loss(reduction="none")
        
        self.step_count = 0
        self.update_count = 0

    def update_target_network(self):
        """Performs a hard copy of online weights to target network."""
        self.target_net.load_state_dict(self.online_net.state_dict())

    def select_action(self, state: np.ndarray, is_safety_task: bool = False, evaluate: bool = False) -> int:
        """
        Selects an action using epsilon-greedy exploration.
        If is_safety_task is True, action indices {1, 2, 3} are masked.
        """
        eps = 0.05 if evaluate else self.epsilon
        
        allowed_actions = list(range(self.action_dim))
        if is_safety_task:
            allowed_actions = [a for a in allowed_actions if a not in [1, 2, 3]]
            
        if self.rng.uniform(0.0, 1.0) < eps:
            return int(self.rng.choice(allowed_actions))
        else:
            state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            self.online_net.eval()
            with torch.no_grad():
                q_values = self.online_net(state_t).squeeze(0)
                
            if is_safety_task:
                masked_q = q_values.clone()
                masked_q[1] = -1e9
                masked_q[2] = -1e9
                masked_q[3] = -1e9
                return int(masked_q.argmax().item())
            else:
                return int(q_values.argmax().item())

    def decay_epsilon(self):
        """Decays exploration parameter epsilon exponentially."""
        self.step_count += 1
        tau = 667.57
        self.epsilon = max(self.epsilon_end, self.epsilon_start * math.exp(-self.step_count / tau))

    def learn(self) -> float:
        """
        Performs a single gradient descent step on a sampled batch of transitions.
        Integrates TD error calculations and prioritized priority updates.
        """
        if len(self.replay_buffer) < self.batch_size:
            return 0.0
            
        # Sample transition batch (includes indices and importance weights)
        states, actions, rewards, next_states, dones, indices, weights = self.replay_buffer.sample(self.batch_size)
        
        self.online_net.train()
        self.target_net.eval()
        
        # Get Q-values for current states
        q_eval = self.online_net(states).gather(dim=-1, index=actions.unsqueeze(-1)).squeeze(-1)
        
        # Double DQN target evaluation
        with torch.no_grad():
            q_online_next = self.online_net(next_states)
            
            # Mask LTE actions (1, 2, 3) in Q_online_next if next state is safety task
            for idx in range(self.batch_size):
                deadline_val = next_states[idx, 10].item()
                if abs(deadline_val - 0.05) < 1e-4:
                    q_online_next[idx, 1] = -1e9
                    q_online_next[idx, 2] = -1e9
                    q_online_next[idx, 3] = -1e9
                    
            best_actions = q_online_next.argmax(dim=-1, keepdim=True)
            
            # Evaluate using target network
            q_target_next = self.target_net(next_states).gather(dim=-1, index=best_actions).squeeze(-1)
            
            # Double-DQN target value
            q_target = rewards + self.gamma * q_target_next * (1.0 - dones)
            
        # Compute element-wise Huber losses
        loss_tensor = self.loss_fn(q_eval, q_target)
        
        # Weighted Huber loss using importance weights
        loss = (loss_tensor * weights).mean()
        
        # Optimize online net
        self.optimizer.zero_grad()
        loss.backward()
        
        # Clip gradients to norm 10
        nn.utils.clip_grad_norm_(self.online_net.parameters(), max_norm=10.0)
        self.optimizer.step()
        
        # Compute TD errors for priority updates
        td_errors = torch.abs(q_eval - q_target).detach().cpu().numpy()
        self.replay_buffer.update_priorities(indices, td_errors)
        
        # Decement exploration
        self.decay_epsilon()
        self.update_count += 1
        
        # Check target network update
        if self.update_count % self.target_update_frequency == 0:
            self.update_target_network()
            
        return float(loss.item())

    def save(self, filepath: str):
        """Saves online network weights checkpoint."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save(self.online_net.state_dict(), filepath)

    def load(self, filepath: str):
        """Loads online and target network weights checkpoint."""
        state_dict = torch.load(filepath)
        self.online_net.load_state_dict(state_dict)
        self.target_net.load_state_dict(state_dict)
