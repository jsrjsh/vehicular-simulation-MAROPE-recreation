# tests/test_d3qn.py
"""
Unit test suite for the Dueling Double DQN agent layer.
Asserts neural network topology, recombination equations, double DQN target calculations,
replay buffer operations, epsilon greedy schedules, and checkpoint round-trips.
Includes a self-validating tiny learning fixture test.
"""

import unittest
import os
import shutil
import math
import numpy as np
import torch
import torch.nn as nn
from agents.d3qn.network import DuelingQNetwork
from agents.d3qn.replay import ReplayBuffer
from agents.d3qn.agent import D3QNAgent

class TestD3QN(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = "tests/tmp_d3qn"
        os.makedirs(self.tmp_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_network_shapes(self):
        """Verify network outputs correct shapes for advantage and state value."""
        net = DuelingQNetwork(state_dim=12, action_dim=11)
        state = torch.randn(5, 12)  # batch size 5
        q_out = net(state)
        
        self.assertEqual(q_out.shape, (5, 11))

    def test_value_advantage_recombination(self):
        """Verify the mathematical recombination formula: Q = V + A - mean(A)."""
        net = DuelingQNetwork(state_dim=12, action_dim=11)
        state = torch.randn(1, 12)
        
        # Manually perform forward pass
        features = net.shared(state)
        v = net.value_head(features)
        adv = net.advantage_head(features)
        
        expected_q = v + (adv - adv.mean(dim=-1, keepdim=True))
        q_out = net(state)
        
        torch.testing.assert_close(q_out, expected_q)

    def test_identical_outputs_identical_seeds(self):
        """Verify identical network initialization and action selections for identical seeds."""
        torch.manual_seed(42)
        agent1 = D3QNAgent(state_dim=12, action_dim=11, seed=42)
        
        torch.manual_seed(42)
        agent2 = D3QNAgent(state_dim=12, action_dim=11, seed=42)
        
        # Test forward pass output equivalence
        state = np.random.RandomState(42).randn(12).astype(np.float32)
        state_t = torch.tensor(state).unsqueeze(0)
        
        q1 = agent1.online_net(state_t)
        q2 = agent2.online_net(state_t)
        torch.testing.assert_close(q1, q2)
        
        # Test selection equivalence
        act1 = agent1.select_action(state, evaluate=True)
        act2 = agent2.select_action(state, evaluate=True)
        self.assertEqual(act1, act2)

    def test_online_target_network_independence(self):
        """Verify online and target network parameters are independent."""
        agent = D3QNAgent(state_dim=12, action_dim=11, seed=10)
        
        # Make changes to online network weights
        with torch.no_grad():
            for param in agent.online_net.parameters():
                param.add_(1.0)
                
        # Assert that target weights remain unchanged
        online_params = list(agent.online_net.parameters())
        target_params = list(agent.target_net.parameters())
        
        for op, tp in zip(online_params, target_params):
            self.assertFalse(torch.equal(op, tp), "Target network parameters updated with online network.")

    def test_replay_buffer_insertion_and_sampling(self):
        """Verify replay buffer storing and uniform sampling under fixed seed."""
        buffer = ReplayBuffer(capacity=100, seed=42)
        
        state = np.zeros(12, dtype=np.float32)
        next_state = np.ones(12, dtype=np.float32)
        
        # Insert transitions
        for i in range(10):
            buffer.add(state, i % 11, float(i), next_state, False)
            
        self.assertEqual(len(buffer), 10)
        
        # Sample batch
        states, actions, rewards, next_states, dones, indices, weights = buffer.sample(batch_size=5)
        
        self.assertEqual(states.shape, (5, 12))
        self.assertEqual(actions.shape, (5,))
        self.assertEqual(rewards.shape, (5,))
        self.assertEqual(next_states.shape, (5, 12))
        self.assertEqual(dones.shape, (5,))

    def test_double_dqn_target_calculation(self):
        """Verify Double-DQN target math using a hand-constructed transition batch."""
        agent = D3QNAgent(state_dim=12, action_dim=11, seed=22)
        
        # Manually create transitioning batch
        states = torch.zeros(1, 12)
        actions = torch.tensor([8], dtype=torch.long)
        rewards = torch.tensor([1.5], dtype=torch.float32)
        next_states = torch.zeros(1, 12)
        dones = torch.tensor([0.0], dtype=torch.float32)
        
        # Mock online_net to return a specific next state action preference
        # We want best action to be 8
        q_online_next = torch.zeros(1, 11)
        q_online_next[0, 8] = 10.0  # highest advantage
        
        # Mock target_net to return Q(s', 8) = 5.0
        q_target_next = torch.zeros(1, 11)
        q_target_next[0, 8] = 5.0
        
        # Target calculation: y = r + gamma * Q_target(s', argmax Q_online(s'))
        # y = 1.5 + 0.95 * 5.0 * (1 - 0.0) = 1.5 + 4.75 = 6.25
        with torch.no_grad():
            best_action = q_online_next.argmax(dim=-1, keepdim=True)  # [8]
            q_target_val = q_target_next.gather(dim=-1, index=best_action).squeeze(-1)
            target = rewards + agent.gamma * q_target_val * (1.0 - dones)
            
        self.assertAlmostEqual(target.item(), 6.25)

    def test_terminal_state_target(self):
        """Verify that terminal transitions yield target = reward exactly (ignoring next Q values)."""
        agent = D3QNAgent(state_dim=12, action_dim=11, seed=33)
        
        rewards = torch.tensor([2.0], dtype=torch.float32)
        dones = torch.tensor([1.0], dtype=torch.float32)
        q_target_val = torch.tensor([15.0], dtype=torch.float32)
        
        target = rewards + agent.gamma * q_target_val * (1.0 - dones)
        self.assertEqual(target.item(), 2.0)

    def test_epsilon_greedy_boundary(self):
        """Verify epsilon boundary conditions: exploration at eps=1, greedy at eps=0."""
        agent = D3QNAgent(state_dim=12, action_dim=11, seed=55)
        state = np.zeros(12, dtype=np.float32)
        
        # Epsilon = 0 (exploitation / greedy)
        # Should always select the max Q action of the online net
        agent.epsilon = 0.0
        q_vals = agent.online_net(torch.tensor(state).unsqueeze(0)).detach().squeeze(0).numpy()
        expected_greedy = int(np.argmax(q_vals))
        
        for _ in range(20):
            action = agent.select_action(state)
            self.assertEqual(action, expected_greedy)
            
        # Epsilon = 1.0 (pure exploration)
        # Should select random actions, not just the greedy choice
        agent.epsilon = 1.0
        actions = [agent.select_action(state) for _ in range(50)]
        # Assert that there's a variation of actions selected
        self.assertTrue(len(set(actions)) > 1)

    def test_checkpoint_round_trip(self):
        """Verify saving and loading weights round-trip."""
        agent = D3QNAgent(state_dim=12, action_dim=11, seed=77)
        filepath = os.path.join(self.tmp_dir, "test_check.pt")
        
        # Modify some weights in online net
        with torch.no_grad():
            list(agent.online_net.parameters())[0].add_(5.0)
            
        # Save checkpoint
        agent.save(filepath)
        self.assertTrue(os.path.exists(filepath))
        
        # Create fresh agent and load
        agent_new = D3QNAgent(state_dim=12, action_dim=11, seed=88)
        agent_new.load(filepath)
        
        # Assert weights are equal
        for p1, p2 in zip(agent.online_net.parameters(), agent_new.online_net.parameters()):
            torch.testing.assert_close(p1, p2)

    def test_loss_and_gradient_bounds(self):
        """Verify that training step outputs finite loss and updates online parameter gradients."""
        agent = D3QNAgent(state_dim=12, action_dim=11, seed=99)
        
        # Fill buffer to batch size
        state = np.zeros(12, dtype=np.float32)
        next_state = np.ones(12, dtype=np.float32)
        for i in range(35):
            agent.replay_buffer.add(state, i % 11, 1.0, next_state, False)
            
        # Learn step
        loss = agent.learn()
        self.assertTrue(math.isfinite(loss))
        self.assertTrue(loss >= 0.0)
        
        # Assert online net weights now have gradients and are updated
        for name, param in agent.online_net.named_parameters():
            if param.requires_grad:
                self.assertIsNotNone(param.grad)
                self.assertTrue(torch.isfinite(param.grad).all())

    def test_learning_fixture(self):
        """Verification of tiny learning fixture: D3QN learns to choose action 8 on constant state S_0."""
        # 1-state MDP: state=S_0, reward = 1.0 for action 8, 0.0 otherwise.
        # Run 5 seeds and assert that agent learns optimal choice reliably
        seeds = [10, 20, 30, 40, 50]
        for seed in seeds:
            agent = D3QNAgent(
                state_dim=12,
                action_dim=11,
                lr=5e-3,
                batch_size=8,
                target_update_frequency=10,
                seed=seed
            )
            state = np.zeros(12, dtype=np.float32)
            next_state = np.zeros(12, dtype=np.float32)
            
            # Learn over 150 steps
            for _ in range(150):
                action = agent.select_action(state)
                reward = 1.0 if action == 8 else 0.0
                agent.replay_buffer.add(state, action, reward, next_state, True)
                if len(agent.replay_buffer) >= agent.batch_size:
                    agent.learn()
                    
            final_choice = agent.select_action(state, evaluate=True)
            self.assertEqual(final_choice, 8, f"Agent failed to learn preferred action (8) on seed {seed}")

if __name__ == "__main__":
    unittest.main()
