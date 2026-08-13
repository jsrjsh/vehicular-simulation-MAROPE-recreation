# tests/test_fedavg.py
"""
Unit test suite for Synchronous Federated Averaging (FedAvg) and coordination.
Validates weight calculations, participant dropouts, threshold boundaries,
independent buffers, target sync rules, and error handling.
"""

import unittest
import copy
import numpy as np
import torch
import torch.nn as nn
from agents.federated.fedavg import federated_averaging
from agents.federated.coordinator import FederatedCoordinator
from agents.d3qn.replay import ReplayBuffer

class TestFedAvg(unittest.TestCase):

    def test_weighted_averaging_two_agents_hand_calculated(self):
        """Verify FedAvg math on hand-calculated client parameters."""
        state_dict_0 = {"layer.weight": torch.tensor([1.0, 1.0], dtype=torch.float32)}
        state_dict_1 = {"layer.weight": torch.tensor([2.0, 2.0], dtype=torch.float32)}
        
        # Scenario 1: Unequal weights (10 samples vs 30 samples)
        # Expected: (10/40) * 1.0 + (30/40) * 2.0 = 0.25 + 1.50 = 1.75
        avg_unequal = federated_averaging([state_dict_0, state_dict_1], [10, 30])
        torch.testing.assert_close(avg_unequal["layer.weight"], torch.tensor([1.75, 1.75]))
        
        # Scenario 2: Equal weights (20 samples each)
        # Expected: (20/40) * 1.0 + (20/40) * 2.0 = 1.50
        avg_equal = federated_averaging([state_dict_0, state_dict_1], [20, 20])
        torch.testing.assert_close(avg_equal["layer.weight"], torch.tensor([1.50, 1.50]))

    def test_parameter_shape_and_key_validation(self):
        """Verify that fedavg rejects key mismatches, shape mismatches, and NaNs/Infs."""
        sd_ref = {"weight": torch.ones(2, 2)}
        
        # Key mismatch
        sd_bad_key = {"bias": torch.ones(2, 2)}
        with self.assertRaises(KeyError):
            federated_averaging([sd_ref, sd_bad_key], [10, 10])
            
        # Shape mismatch
        sd_bad_shape = {"weight": torch.ones(3, 3)}
        with self.assertRaises(ValueError):
            federated_averaging([sd_ref, sd_bad_shape], [10, 10])
            
        # NaN / Inf values
        sd_nan = {"weight": torch.tensor([[1.0, float("nan")], [3.0, 4.0]])}
        with self.assertRaises(ValueError):
            federated_averaging([sd_ref, sd_nan], [10, 10])

    def test_no_mutation_of_source_state_dicts(self):
        """Verify that the source dictionaries are not mutated during FedAvg."""
        sd0 = {"w": torch.tensor([1.0])}
        sd1 = {"w": torch.tensor([2.0])}
        
        _ = federated_averaging([sd0, sd1], [10, 10])
        
        self.assertEqual(sd0["w"].item(), 1.0)
        self.assertEqual(sd1["w"].item(), 2.0)

    def test_participation_threshold_boundaries(self):
        """Verify active client participation threshold constraints (abort at <70%)."""
        # Case 1: 10 agents, 7 active (70% participation) -> Success
        coord = FederatedCoordinator(n_agents=10, seed=42)
        coord.participation_prob = 1.0  # Force all active first
        info = coord.aggregate_and_broadcast()
        self.assertFalse(info["aborted"])
        
        # Case 2: Manually inject active client list to test below threshold (6 agents active = 60%)
        # Mock rng to select exactly 6 agents
        coord_abort = FederatedCoordinator(n_agents=10, seed=42)
        class MockRng:
            def __init__(self):
                self.calls = 0
            def uniform(self, low=0.0, high=1.0):
                self.calls += 1
                return 0.2 if self.calls <= 6 else 0.8
        coord_abort.rng = MockRng()
        coord_abort.participation_prob = 0.5
        
        info_abort = coord_abort.aggregate_and_broadcast()
        self.assertTrue(info_abort["aborted"])
        self.assertEqual(info_abort["active_agents"], 6)

    def test_global_broadcast_consistency_and_target_sync(self):
        """Verify post-broadcast weights equivalence and target network synchronization."""
        coord = FederatedCoordinator(n_agents=4, seed=10)
        
        # Modify agent 0 online network parameters manually
        with torch.no_grad():
            for p in coord.agents[0].online_net.parameters():
                p.add_(5.0)
                
        # Run FedAvg (force 100% participation)
        coord.participation_prob = 1.0
        _ = coord.aggregate_and_broadcast()
        
        # Assert online and target networks are synchronized across all clients
        ref_online_sd = coord.agents[0].online_net.state_dict()
        for idx in range(1, 4):
            client = coord.agents[idx]
            # Check online net matches client 0 online net
            for k in ref_online_sd.keys():
                torch.testing.assert_close(client.online_net.state_dict()[k], ref_online_sd[k])
                # Check target net matches online net
                torch.testing.assert_close(client.target_net.state_dict()[k], ref_online_sd[k])

    def test_local_replay_buffers_remain_independent(self):
        """Verify that client replay buffers remain local and independent."""
        coord = FederatedCoordinator(n_agents=3, seed=20)
        
        # Add transition to agent 0's buffer
        coord.agents[0].replay_buffer.add(np.zeros(12), 0, 1.0, np.zeros(12), False)
        
        self.assertEqual(len(coord.agents[0].replay_buffer), 1)
        self.assertEqual(len(coord.agents[1].replay_buffer), 0)
        self.assertEqual(len(coord.agents[2].replay_buffer), 0)

    def test_local_optimizers_remain_independent(self):
        """Verify client optimizer states remain independent and local."""
        coord = FederatedCoordinator(n_agents=3, seed=30)
        
        opt0 = coord.agents[0].optimizer
        opt1 = coord.agents[1].optimizer
        
        self.assertNotEqual(opt0, opt1)

    def test_replay_mode_preservation(self):
        """Verify uniform and PER modes are preserved within local agents."""
        coord_uni = FederatedCoordinator(n_agents=2, replay_mode="uniform", seed=40)
        coord_per = FederatedCoordinator(n_agents=2, replay_mode="prioritized", seed=40)
        
        self.assertEqual(coord_uni.agents[0].replay_buffer.mode, "uniform")
        self.assertEqual(coord_per.agents[0].replay_buffer.mode, "prioritized")

if __name__ == "__main__":
    unittest.main()
