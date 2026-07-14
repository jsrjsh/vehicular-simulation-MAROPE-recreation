# agents/federated/coordinator.py
"""
Federated Learning coordinator orchestrating local training epochs,
client participation dropout schedules, LDP weight clipping/noising,
and bytes accounting.
"""

import io
import copy
import numpy as np
import torch
import torch.optim as optim
from agents.d3qn.agent import D3QNAgent
from agents.federated.fedavg import federated_averaging
from agents.privacy.gaussian_ldp import apply_gaussian_ldp

class FederatedCoordinator:
    """
    Orchestrates the synchronous FedAvg process across multiple vehicular agents.
    Supports Local Differential Privacy (LDP) update clipping and Gaussian noise perturbation.
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
                 privacy_mode: str = "none",
                 clip_norm: float = 1.0,
                 noise_multiplier: float = 0.0,
                 seed: int = None):
        
        self.n_agents = n_agents
        self.participation_prob = participation_prob
        self.privacy_mode = privacy_mode
        self.clip_norm = clip_norm
        self.noise_multiplier = noise_multiplier
        self.seed_val = seed
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
        
        # Privacy tracking metrics per round
        self.privacy_logs = []
        
        # Model parameter metrics (calculated once)
        dummy_agent = self.agents[0]
        self.param_count = sum(p.numel() for p in dummy_agent.online_net.parameters())
        
        bio = io.BytesIO()
        torch.save(dummy_agent.online_net.state_dict(), bio)
        self.serialized_size_bytes = len(bio.getvalue())

    def aggregate_and_broadcast(self) -> dict:
        """
        Runs one synchronous aggregation round.
        Computes local updates relative to the previous global model, clips/noises them
        if privacy_mode is active, aggregates updates, and broadcasts the global model.
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
            "active_indices": active_indices,
            "clients": {}
        }
        
        if participation_ratio < 0.70:
            self.aborted_rounds += 1
            round_info["aborted"] = True
            print(f"[FedAvg Round {self.sync_rounds}] ABORTED (Participation {participation_ratio*100:.1f}% < 70% threshold)")
            return round_info
            
        # Previous global model (taken from client 0 since they are synchronized)
        global_prev = copy.deepcopy(self.agents[0].online_net.state_dict())
        
        delta_list = []
        sample_counts = []
        
        for idx in active_indices:
            agent = self.agents[idx]
            # Compute update Delta_i = w_i - w_global_prev
            delta = {}
            for k in global_prev.keys():
                delta[k] = agent.online_net.state_dict()[k] - global_prev[k]
                
            if self.privacy_mode == "ldp_gaussian":
                # Deterministic noise under fixed seed: base_seed + client_idx + round * 1000
                base_seed = self.seed_val if self.seed_val is not None else 42
                priv_seed = base_seed + idx + self.sync_rounds * 1000
                
                private_delta, raw_norm, clipped_norm, noise_norm, snr, clipped = apply_gaussian_ldp(
                    update_state_dict=delta,
                    clip_norm=self.clip_norm,
                    noise_multiplier=self.noise_multiplier,
                    seed=priv_seed
                )
                delta_list.append(private_delta)
                
                # Log metrics
                client_stats = {
                    "raw_norm": raw_norm,
                    "clipped_norm": clipped_norm,
                    "noise_norm": noise_norm,
                    "snr": snr,
                    "clipped": clipped
                }
                round_info["clients"][idx] = client_stats
            else:
                # Privacy Mode: None
                delta_list.append(delta)
                
            sample_counts.append(agent.batch_size)
            
        # Aggregate privatized/raw updates
        delta_global = federated_averaging(delta_list, sample_counts)
        
        # Construct new global model: w_global_new = w_global_prev + delta_global
        global_new = {}
        for k in global_prev.keys():
            global_new[k] = global_prev[k] + delta_global[k]
            
        # Broadcast global weights to all clients
        for idx, agent in enumerate(self.agents):
            agent.online_net.load_state_dict(global_new)
            # Reinitialize optimizer to clear momentum states
            agent.optimizer = optim.Adam(agent.online_net.parameters(), lr=agent.optimizer.param_groups[0]['lr'])
            # Synchronize client target networks locally
            agent.update_target_network()
            
        # Calculate communications bytes
        upload_bytes = len(active_indices) * self.serialized_size_bytes
        broadcast_bytes = self.n_agents * self.serialized_size_bytes
        round_bytes = upload_bytes + broadcast_bytes
        
        self.cum_bytes += round_bytes
        self.cum_uploads += upload_bytes
        self.cum_broadcasts += broadcast_bytes
        
        round_info["bytes_transferred"] = round_bytes
        
        # Save round metrics to privacy logs
        self.privacy_logs.append(round_info)
        
        print(f"[FedAvg Round {self.sync_rounds}] SUCCESS (Active agents: {len(active_indices)}/{self.n_agents}, Bytes: {round_bytes/1024:.2f} KB)")
        return round_info
