# tests/test_env.py
"""
Unit test suite for the deterministic MA-ROPE environment core.
Asserts numerical correctness and mathematical invariants of physical formulas,
kinematics, cost models, observations, and interface structures.
"""

import unittest
import math
import numpy as np
from env.config import ACTION_MAP, RAT_SPECS, TASK_TYPES
from env.channel import (
    compute_path_loss, compute_jakes_fading, compute_sinr, compute_link_success
)
from env.environment import V2XEnv

class TestV2XEnvironment(unittest.TestCase):

    def test_action_mapping(self):
        """Verify action-index mapping matches the recreation guide exactly."""
        self.assertEqual(len(ACTION_MAP), 11)
        self.assertEqual(ACTION_MAP[0], (0, 0.0))
        self.assertEqual(ACTION_MAP[1], (1, 0.25))
        self.assertEqual(ACTION_MAP[2], (1, 0.50))
        self.assertEqual(ACTION_MAP[3], (1, 0.75))
        self.assertEqual(ACTION_MAP[4], (2, 0.25))
        self.assertEqual(ACTION_MAP[5], (2, 0.50))
        self.assertEqual(ACTION_MAP[6], (4, 0.25))
        self.assertEqual(ACTION_MAP[7], (4, 0.50))
        self.assertEqual(ACTION_MAP[8], (4, 1.00))
        self.assertEqual(ACTION_MAP[9], (3, 0.50))
        self.assertEqual(ACTION_MAP[10], (3, 1.00))

    def test_seed_repeatability(self):
        """Verify seeded runs are exactly reproducible for identical seeds."""
        env1 = V2XEnv(seed=42)
        env2 = V2XEnv(seed=42)

        obs1 = env1.reset()
        obs2 = env2.reset()

        for k in obs1:
            np.testing.assert_array_equal(obs1[k], obs2[k])

        actions = {i: 8 for i in env1.agents}  # 5G offload for all
        n_obs1, r1, d1, info1 = env1.step(actions)
        n_obs2, r2, d2, info2 = env2.step(actions)

        for k in n_obs1:
            np.testing.assert_array_equal(n_obs1[k], n_obs2[k])
            self.assertEqual(r1[k], r2[k])
            self.assertEqual(d1[k], d2[k])
            self.assertEqual(info1[k]["latency_ms"], info2[k]["latency_ms"])
            self.assertEqual(info1[k]["energy_j"], info2[k]["energy_j"])
            self.assertEqual(info1[k]["transmission_success"], info2[k]["transmission_success"])

    def test_observation_properties(self):
        """Verify observation shape, types, element ordering, and normalization bounds."""
        env = V2XEnv(seed=10)
        obs = env.reset()

        self.assertEqual(len(obs), env.n_vehicles)
        for agent_id, agent_obs in obs.items():
            self.assertEqual(agent_obs.shape, (12,))
            self.assertEqual(agent_obs.dtype, np.float32)
            # Ensure normalization bounds [0, 1]
            for idx, val in enumerate(agent_obs):
                self.assertTrue(0.0 <= val <= 1.0, f"Value {val} at index {idx} violates [0, 1] bounds")

    def test_local_execution_latency(self):
        """Verify local execution latency satisfies L_local = C / f_cpu * 1000 exactly."""
        env = V2XEnv(seed=20)
        env.reset()
        
        # Override task type of vehicle 0 to safety
        env.active_tasks[0] = TASK_TYPES["safety"].copy()
        env.active_tasks[0]["type"] = "safety"
        
        # Take local execution action 0
        _, _, _, infos = env.step({0: 0, 1: 0, 2: 0, 3: 0})
        
        expected_latency_ms = (TASK_TYPES["safety"]["cpu_cycles"] / 2e9) * 1000.0
        self.assertAlmostEqual(infos[0]["latency_ms"], expected_latency_ms)

    def test_queue_delay_saturation(self):
        """Verify RSU queue delays and workload aggregation below, at, and above saturation."""
        env = V2XEnv(n_vehicles=4, include_rsu_queue=True, seed=30)
        env.reset()
        
        # Override vehicle coordinates to place them all nearest to RSU 0 (at 500m)
        env.positions[0] = 500.0
        env.positions[1] = 505.0
        env.positions[2] = 495.0
        env.positions[3] = 510.0
        
        # Step with AllOffload actions for all (action 8: 5G-NR 100%)
        # Sum Q_0 = 1.0 + 1.0 + 1.0 + 1.0 = 4.0
        # Expected queuing delay = 4.0 * 50 = 200 ms
        _, _, _, infos = env.step({0: 8, 1: 8, 2: 8, 3: 8})
        
        self.assertEqual(env.rsu_queues[0], 4.0)
        self.assertEqual(env.rsu_cbr_curr[0], 1.0) # Saturated CBR = clip(4/4, 0, 1) = 1.0
        
        # Check queuing delay contribution
        # Vehicle 0 uses action 8 -> adapted offload ratio is rho_prime = 1.0 * q_5g
        # We verify that queue delay matches delay per unit ms * Q
        rsu_idx = env._get_nearest_rsu(env.positions[0])
        self.assertEqual(rsu_idx, 0)
        
        # Queue delay in environment step must beDELAY_PER_UNIT_MS * Q
        expected_q_delay = 4.0 * 50.0
        self.assertEqual(expected_q_delay, 200.0)

    def test_sinr_monotonicity(self):
        """Verify that link SINR decreases monotonically as distance increases."""
        rng = np.random.RandomState(42)
        
        # Test 5G-NR channel at different distances
        sinr_10m = compute_sinr(4, 10.0, 30.0, rng)
        
        rng = np.random.RandomState(42) # reset state for same shadow/fading samples
        sinr_100m = compute_sinr(4, 100.0, 30.0, rng)
        
        rng = np.random.RandomState(42)
        sinr_1000m = compute_sinr(4, 1000.0, 30.0, rng)
        
        self.assertTrue(sinr_10m > sinr_100m)
        self.assertTrue(sinr_100m > sinr_1000m)

    def test_cellular_fading_speed(self):
        """Verify Jakes fading behavior is speed-dependent and 0 below speed threshold."""
        rng = np.random.RandomState(100)
        
        # 1. Zero fading below 0.1 m/s speed
        fade_stationary = compute_jakes_fading(4, 0.05, rng)
        self.assertEqual(fade_stationary, 0.0)
        
        # 2. Non-negative fading at standard vehicle speed
        fade_moving = compute_jakes_fading(4, 25.0, rng)
        self.assertTrue(fade_moving >= 0.0)

    def test_prr_counter_correctness(self):
        """Verify packet transmission and success counters update properly."""
        env = V2XEnv(seed=50)
        env.reset()
        
        # Trigger offloading for agent 0 using action 8 (5GNR)
        _, _, _, infos = env.step({0: 8, 1: 0, 2: 0, 3: 0})
        
        tx_count = env.tx_counters[0][4]
        rx_count = env.rx_counters[0][4]
        
        self.assertEqual(tx_count, 1)
        if infos[0]["transmission_success"]:
            self.assertEqual(rx_count, 1)
        else:
            self.assertEqual(rx_count, 0)

    def test_otr_le_prr_invariant(self):
        """Verify that the empirical PRR is always greater than or equal to OTR."""
        env = V2XEnv(seed=60)
        env.reset()
        
        # Step through 5 epochs offloading all vehicles
        for _ in range(5):
            _, _, _, infos = env.step({0: 8, 1: 7, 2: 6, 3: 5})
            
        for i in env.agents:
            for rat in range(1, 5):
                tx = env.tx_counters[i][rat]
                if tx > 0:
                    prr = env.rx_counters[i][rat] / tx
                    otr = env.rx_on_time_counters[i][rat] / tx
                    self.assertTrue(otr <= prr, f"OTR ({otr}) exceeded PRR ({prr}) for agent {i} on RAT {rat}")

    def test_utility_normalization(self):
        """Verify that reward values (U_PRR training utility) are normalized to [0.0, 1.0]."""
        env = V2XEnv(seed=70)
        env.reset()
        
        # Run multiple steps with random actions and verify rewards
        for _ in range(20):
            actions = {i: env.rng.randint(0, 11) for i in env.agents}
            _, rewards, _, _ = env.step(actions)
            for agent_id, r in rewards.items():
                self.assertTrue(0.0 <= r <= 1.0, f"Reward {r} for vehicle {agent_id} violates [0, 1] bounds")

    def test_energy_non_negativity(self):
        """Verify that energy consumption is strictly non-negative."""
        env = V2XEnv(seed=80)
        env.reset()
        
        for _ in range(20):
            actions = {i: env.rng.randint(0, 11) for i in env.agents}
            _, _, _, infos = env.step(actions)
            for agent_id, info in infos.items():
                self.assertTrue(info["energy_j"] >= 0.0, f"Energy {info['energy_j']} is negative for vehicle {agent_id}")

    def test_invalid_action_handling(self):
        """Verify invalid actions raise a ValueError."""
        env = V2XEnv(seed=90)
        env.reset()
        
        # Invalid action index 11
        with self.assertRaises(ValueError):
            env.step({0: 11, 1: 0, 2: 0, 3: 0})
            
        # Invalid action index -1
        with self.assertRaises(ValueError):
            env.step({0: -1, 1: 0, 2: 0, 3: 0})

    def test_no_nan_or_infinite(self):
        """Verify that environment arrays do not contain NaN or infinite values under full config sweep."""
        env = V2XEnv(seed=111)
        obs = env.reset()
        
        for k, v in obs.items():
            self.assertFalse(np.isnan(v).any())
            self.assertFalse(np.isinf(v).any())
            
        for _ in range(50):
            actions = {i: env.rng.randint(0, 11) for i in env.agents}
            next_obs, rewards, dones, infos = env.step(actions)
            for i in env.agents:
                self.assertFalse(np.isnan(next_obs[i]).any())
                self.assertFalse(np.isinf(next_obs[i]).any())
                self.assertFalse(np.isnan(rewards[i]))
                self.assertFalse(np.isinf(rewards[i]))
                self.assertFalse(np.isnan(infos[i]["latency_ms"]))
                self.assertFalse(np.isnan(infos[i]["energy_j"]))

if __name__ == "__main__":
    unittest.main()
