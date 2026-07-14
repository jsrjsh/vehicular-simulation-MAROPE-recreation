# agents/federated/coordinator.py
"""
Federated Learning coordinator orchestrating local training epochs,
client participation dropout schedules, weight aggregation, and bytes accounting.
"""

import io
import copy
import numpy as np
import torch
import torch.optim as optim
from agents.d3qn.agent import D3QNAgent
from agents.federated.fedavg import federated_averaging

class FederatedCoordinator:
    """
    Orchestrates the synchronous FedAvg process across multiple vehicular agents.
    Maintains independent agents, replay buffers, and optimizer instances.
    """
    def __init__(self,
                 n_agents: int = 4,
                 state_dim: int = 12,
                 action_dim: int = 11,
                 gamma: float = 0.95,
                 lr: float = 1e-3,
                 buffer_capacity: int = 5000,
                 batch_size: int = 32,
                 target_update_frequency: int = 100,
                 epsilon_start: float = 1.0,
                 epsilon_end: float = 0.05,
                 epsilon_decay_steps: int = 2000,
                 replay_mode: str = "uniform",
                 participation_prob: float = 0.9,
                 seed: int = None):
        
        self.n_agents = n_agents
        self.participation_prob = participation_prob
        self.rng = np.random.RandomState(seed)
        
        # Initialize independent client agents
        self.agents = []
        for i in range(n_agents):
            client_seed = seed + i if seed is not None else None
            self.agents.append(
                D3QNAgent(
                    state_dim=state_dim,
                    action_dim=action_dim,
                    gamma=gamma,
                    lr=lr,
                    buffer_capacity=buffer_capacity,
                    batch_size=batch_size,
                    target_update_frequency=target_update_frequency,
                    epsilon_start=epsilon_start,
                    epsilon_end=epsilon_end,
                    epsilon_decay_steps=epsilon_decay_steps,
                    replay_mode=replay_mode,
                    seed=client_seed
                )
            )
            
        # Communication accounting stats
        self.cum_bytes = 0
        self.cum_uploads = 0
        self.cum_broadcasts = 0
        self.sync_rounds = 0
        self.aborted_rounds = 0
        
        # Model parameter metrics (calculated once)
        dummy_agent = self.agents[0]
        self.param_count = sum(p.numel() for p in dummy_agent.online_net.parameters())
        
        bio = io.BytesIO()
        torch.save(dummy_agent.online_net.state_dict(), bio)
        self.serialized_size_bytes = len(bio.getvalue())

    def aggregate_and_broadcast(self) -> dict:
        """
        Runs one synchronous aggregation round.
        Selects active participants based on participation probability.
        If participant count drops below 70% threshold, aborts the round.
        """
        self.sync_rounds += 1
        
        # Determine participating client agents
        active_indices = []
        for i in range(self.n_agents):
            if self.rng.uniform(0.0, 1.0) < self.participation_prob:
                active_indices.append(i)
                
        participation_ratio = len(active_indices) / self.n_agents
        
        # Log participation
        round_info = {
            "round": self.sync_rounds,
            "total_agents": self.n_agents,
            "active_agents": len(active_indices),
            "ratio": participation_ratio,
            "aborted": False,
            "bytes_transferred": 0,
            "active_indices": active_indices
        }
        
        if participation_ratio < 0.70:
            # Abort the round: clients retain local weights
            self.aborted_rounds += 1
            round_info["aborted"] = True
            print(f"[FedAvg Round {self.sync_rounds}] ABORTED (Participation {participation_ratio*100:.1f}% < 70% threshold)")
            return round_info
            
        # Extract participant state dictionaries and local sample counts
        state_dicts = []
        sample_counts = []
        
        for idx in active_indices:
            agent = self.agents[idx]
            state_dicts.append(agent.online_net.state_dict())
            # For weighting, we use the local batch sample steps
            sample_counts.append(agent.batch_size)
            
        # Perform Federated Averaging
        global_state = federated_averaging(state_dicts, sample_counts)
        
        # Broadcast global weights to all clients
        for agent in self.agents:
            agent.online_net.load_state_dict(global_state)
            # Reinitialize optimizer to clear historical momentum coordinates
            # Keep original learning rate from client
            agent.optimizer = optim.Adam(agent.online_net.parameters(), lr=agent.online_net.shared[0].weight.grad is None and 1e-3 or agent.optimizer.param_groups[0]['lr'])
            # Locally update target network weights
            agent.update_target_network()
            
        # Calculate communications bytes
        # Byte footprint: Uploads (active_agents * size) + Broadcasts (n_agents * size)
        upload_bytes = len(active_indices) * self.serialized_size_bytes
        broadcast_bytes = self.n_agents * self.serialized_size_bytes
        round_bytes = upload_bytes + broadcast_bytes
        
        self.cum_bytes += round_bytes
        self.cum_uploads += upload_bytes
        self.cum_broadcasts += broadcast_bytes
        
        round_info["bytes_transferred"] = round_bytes
        print(f"[FedAvg Round {self.sync_rounds}] SUCCESS (Active agents: {len(active_indices)}/{self.n_agents}, Bytes: {round_bytes/1024:.2f} KB)")
        return round_info
