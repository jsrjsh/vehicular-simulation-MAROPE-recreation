# tests/test_per.py
"""
Unit test suite for Prioritized Experience Replay (PER) buffer.
Verifies sample distributions, alpha/beta scaling bounds, normalization correctness,
importance-sampling weight values, deterministic reproducibility, and ring buffer wraps.
"""

import unittest
import numpy as np
import torch
import torch.nn as nn
from agents.d3qn.replay import ReplayBuffer

class TestPER(unittest.TestCase):

    def test_buffer_insertion_and_wraparound(self):
        """Verify insertion limits and index wraparounds for ring-buffer storage."""
        buffer = ReplayBuffer(capacity=5, mode="prioritized", seed=42)
        
        # Test inserting into empty buffer
        buffer.add(np.zeros(12), 0, 1.0, np.zeros(12), False)
        self.assertEqual(len(buffer), 1)
        self.assertEqual(buffer.pos, 1)
        self.assertEqual(buffer.priorities[0], 1.0)
        
        # Fill buffer to capacity
        for i in range(1, 5):
            buffer.add(np.zeros(12), i, 1.0, np.zeros(12), False)
        self.assertEqual(len(buffer), 5)
        self.assertEqual(buffer.pos, 0)  # pos wraps back to start for next insertion
        
        # Overwrite oldest elements
        buffer.add(np.ones(12), 5, 2.0, np.ones(12), True)
        self.assertEqual(len(buffer), 5)
        self.assertEqual(buffer.pos, 1)
        # Verify first transition is overwritten
        s, a, r, ns, d = buffer.buffer[0]
        self.assertTrue(np.allclose(s, np.ones(12)))
        self.assertEqual(a, 5)
        self.assertEqual(r, 2.0)
        self.assertEqual(d, True)

    def test_priority_epsilon_guard(self):
        """Verify that zero TD error still receives a small positive priority."""
        buffer = ReplayBuffer(capacity=10, mode="prioritized", seed=42)
        buffer.add(np.zeros(12), 0, 1.0, np.zeros(12), False)
        
        # Update priority with 0.0 TD error
        buffer.update_priorities(np.array([0]), np.array([0.0]))
        # BUGFIX (Claude, 2026-08-02): priorities is a numpy.float32 array, and 1e-6 is not
        # exactly representable in float32 (rounds to 9.9999997...e-07), so assertEqual against
        # the float64 literal 1e-6 fails on a pure precision artifact, not a logic error. Use a
        # tolerance-based comparison instead.
        self.assertAlmostEqual(float(buffer.priorities[0]), 1e-6, places=6)

    def test_alpha_zero_uniform_approximation(self):
        """Verify that alpha = 0.0 makes sampling probabilities strictly uniform."""
        buffer = ReplayBuffer(capacity=5, mode="prioritized", alpha=0.0, seed=42)
        
        # Insert transitions with highly disparate priorities
        for i in range(5):
            buffer.add(np.zeros(12), i, 1.0, np.zeros(12), False)
            
        # Manually alter priorities
        buffer.priorities[0] = 100.0
        buffer.priorities[1] = 0.01
        
        # Sample multiple times and check counts
        counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        for _ in range(1000):
            _, _, _, _, _, indices, _ = buffer.sample(batch_size=1)
            counts[indices[0]] += 1
            
        # Under alpha=0, sampling probabilities should be identical (each ~200 samples)
        for idx, count in counts.items():
            self.assertTrue(140 < count < 260, f"Index {idx} sampled {count} times (not uniform).")

    def test_prioritization_sampling_bias(self):
        """Verify that higher-priority transitions are sampled more frequently."""
        buffer = ReplayBuffer(capacity=5, mode="prioritized", alpha=1.0, seed=42)
        
        # Add 5 transitions
        for i in range(5):
            buffer.add(np.zeros(12), i, 1.0, np.zeros(12), False)
            
        # Update priorities so index 2 has very high priority, others have baseline
        # P(2) = 10.0 / 14.0 = 0.714
        # P(others) = 1.0 / 14.0 = 0.071
        buffer.priorities[2] = 10.0
        buffer.priorities[0] = 1.0
        buffer.priorities[1] = 1.0
        buffer.priorities[3] = 1.0
        buffer.priorities[4] = 1.0
        
        counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        for _ in range(1000):
            _, _, _, _, _, indices, _ = buffer.sample(batch_size=1)
            counts[indices[0]] += 1
            
        # Index 2 should be sampled around 700 times, others around 70 times
        self.assertTrue(counts[2] > 600)
        self.assertTrue(counts[0] < 120)

    def test_beta_weight_corrections(self):
        """Verify that beta=0 yields equal weights (1.0), and beta=1 yields full correction."""
        # 1. beta = 0.0
        buffer_b0 = ReplayBuffer(capacity=5, mode="prioritized", alpha=1.0, beta_start=0.0, beta_end=0.0, seed=42)
        for i in range(5):
            buffer_b0.add(np.zeros(12), i, 1.0, np.zeros(12), False)
        buffer_b0.priorities[0] = 10.0
        buffer_b0.priorities[1] = 1.0
        
        _, _, _, _, _, _, weights = buffer_b0.sample(batch_size=4)
        # All weights should be exactly 1.0
        self.assertTrue(np.allclose(weights.numpy(), 1.0))
        
        # 2. beta = 1.0
        # Under beta=1.0, weights should fully correct for bias: w_i = (N * P(i))^-1
        # P(i) is proportional to priority_i^alpha
        # Max weight should be normalized to 1.0
        buffer_b1 = ReplayBuffer(capacity=2, mode="prioritized", alpha=1.0, beta_start=1.0, beta_end=1.0, seed=42)
        buffer_b1.add(np.zeros(12), 0, 1.0, np.zeros(12), False)
        buffer_b1.add(np.zeros(12), 1, 1.0, np.zeros(12), False)
        
        buffer_b1.priorities[0] = 2.0  # prob P(0) = 2/3
        buffer_b1.priorities[1] = 1.0  # prob P(1) = 1/3
        
        # Sample the whole buffer
        _, _, _, _, _, indices, weights = buffer_b1.sample(batch_size=2)
        # Weights: w_0 = (2 * 2/3)^-1 = 3/4 = 0.75
        #          w_1 = (2 * 1/3)^-1 = 3/2 = 1.5
        # Normalized by max weight (1.5):
        #          w_0_norm = 0.75 / 1.5 = 0.5
        #          w_1_norm = 1.5 / 1.5 = 1.0
        # Let's map indices to weights
        weights_dict = {indices[i].item(): weights[i].item() for i in range(2)}
        self.assertAlmostEqual(weights_dict[0], 0.5)
        self.assertAlmostEqual(weights_dict[1], 1.0)

    def test_weighted_loss_hand_calculation(self):
        """Verify element-wise loss scaling matches a hand-calculated weighted Huber loss step."""
        loss_fn = nn.SmoothL1Loss(reduction="none")
        
        q_eval = torch.tensor([1.0, 3.0], dtype=torch.float32)
        q_target = torch.tensor([2.0, 3.0], dtype=torch.float32)
        weights = torch.tensor([0.5, 1.0], dtype=torch.float32)
        
        # Huber Loss:
        # l_0: |1.0 - 2.0| = 1.0. For diff <= 1, loss is 0.5 * diff^2 = 0.5
        # l_1: |3.0 - 3.0| = 0.0. Loss is 0.0
        # Weighted loss: (0.5 * 0.5 + 0.0 * 1.0) / 2 = 0.25 / 2 = 0.125
        loss_tensor = loss_fn(q_eval, q_target)
        weighted_loss = (loss_tensor * weights).mean()
        
        self.assertEqual(weighted_loss.item(), 0.125)

    def test_deterministic_seeding(self):
        """Verify sampling reproducibility under fixed seeds."""
        buf1 = ReplayBuffer(capacity=100, mode="prioritized", seed=123)
        buf2 = ReplayBuffer(capacity=100, mode="prioritized", seed=123)
        
        for i in range(50):
            state = np.random.randn(12).astype(np.float32)
            buf1.add(state, i%11, 1.0, state, False)
            buf2.add(state, i%11, 1.0, state, False)
            
        # Give varying priorities
        buf1.priorities[:50] = np.random.RandomState(42).uniform(0.1, 10.0, size=50)
        buf2.priorities[:50] = np.random.RandomState(42).uniform(0.1, 10.0, size=50)
        
        # Sample batches
        _, _, _, _, _, ind1, w1 = buf1.sample(batch_size=10)
        _, _, _, _, _, ind2, w2 = buf2.sample(batch_size=10)
        
        np.testing.assert_array_equal(ind1, ind2)
        torch.testing.assert_close(w1, w2)

    def test_uniform_mode_preserves_weights_one(self):
        """Verify that uniform mode returns flat weight arrays of 1.0."""
        buf = ReplayBuffer(capacity=10, mode="uniform", seed=99)
        for i in range(10):
            buf.add(np.zeros(12), i%11, 1.0, np.zeros(12), False)
            
        # Sample batch
        _, _, _, _, _, _, weights = buf.sample(batch_size=5)
        self.assertTrue(np.allclose(weights.numpy(), 1.0))

if __name__ == "__main__":
    unittest.main()
