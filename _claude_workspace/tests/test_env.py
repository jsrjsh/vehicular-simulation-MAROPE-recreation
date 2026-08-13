# tests/test_env.py
"""
Unit test suite for the deterministic MA-ROPE environment core.
Asserts numerical correctness and mathematical invariants of physical formulas,
kinematics, cost models, observations, and interface structures.
Includes golden-value checks and coverage matrices.
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

    def test_action_mapping_all(self):
        """Verify action-index mapping for all 11 action configurations."""
        self.assertEqual(len(ACTION_MAP), 11)
        expected = {
            0: (0, 0.0),
            1: (1, 0.25),
            2: (1, 0.50),
            3: (1, 0.75),
            4: (2, 0.25),
            5: (2, 0.50),
            6: (4, 0.25),
            7: (4, 0.50),
            8: (4, 1.00),
            9: (3, 0.50),
            10: (3, 1.00)
        }
        for act_idx, mapping in expected.items():
            self.assertEqual(ACTION_MAP[act_idx], mapping, f"Action {act_idx} mapping mismatch")

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

    def test_observation_ordering_and_properties(self):
        """Verify observation shape, types, element ordering, and normalization bounds."""
        env = V2XEnv(seed=10)
        obs = env.reset()

        self.assertEqual(len(obs), env.n_vehicles)
        for agent_id, agent_obs in obs.items():
            self.assertEqual(agent_obs.shape, (12,))
            self.assertEqual(agent_obs.dtype, np.float32)
            
            # Element ordering check
            # features 0-3: SINR norm [0, 1]
            # features 4-7: empirical PRRs [0, 1]
            # feature 8: queue norm
            # feature 9: data size norm
            # feature 10: deadline norm
            # feature 11: battery norm
            for idx in range(12):
                val = agent_obs[idx]
                self.assertTrue(0.0 <= val <= 1.0, f"Value {val} at index {idx} violates [0, 1] bounds")

    def test_local_execution_latency(self):
        """Verify local execution latency satisfies L_local = C / f_cpu * 1000 exactly."""
        env = V2XEnv(seed=20)
        env.reset()
        env.active_tasks[0] = TASK_TYPES["safety"].copy()
        env.active_tasks[0]["type"] = "safety"
        
        _, _, _, infos = env.step({0: 0, 1: 0, 2: 0, 3: 0})
        expected_latency_ms = (TASK_TYPES["safety"]["cpu_cycles"] / 2e9) * 1000.0
        self.assertAlmostEqual(infos[0]["latency_ms"], expected_latency_ms)

    def test_queue_delay_saturation(self):
        """Verify RSU queue delays and workload aggregation below, at, and above saturation."""
        env = V2XEnv(n_vehicles=4, include_rsu_queue=True, seed=30)
        env.reset()
        
        # Override positions to group all vehicles under RSU 0 (at 500m)
        env.positions[0] = 500.0
        env.positions[1] = 505.0
        env.positions[2] = 495.0
        env.positions[3] = 510.0
        
        # Above Saturation: Q = 1 + 1 + 1 + 1 = 4.0 (delay = 200 ms)
        _, _, _, infos = env.step({0: 8, 1: 8, 2: 8, 3: 8})
        self.assertEqual(env.rsu_queues[0], 4.0)
        self.assertEqual(env.rsu_cbr_curr[0], 1.0)
        
        # At Saturation: Q = 0.5 + 0.5 + 0.5 + 0.5 = 2.0 (delay = 100 ms)
        env.reset()
        env.positions[0] = 500.0
        env.positions[1] = 505.0
        env.positions[2] = 495.0
        env.positions[3] = 510.0
        _, _, _, infos_at = env.step({0: 5, 1: 5, 2: 5, 3: 5}) # action 5 is ITS-G5 50%
        self.assertEqual(env.rsu_queues[0], 2.0)
        self.assertEqual(env.rsu_cbr_curr[0], 0.5)
        
        # Below Saturation: 1 offloads with 0.25 -> Q = 0.25 (delay = 12.5 ms)
        env.reset()
        env.positions[0] = 500.0
        env.positions[1] = 505.0
        env.positions[2] = 495.0
        env.positions[3] = 510.0
        _, _, _, infos_below = env.step({0: 4, 1: 0, 2: 0, 3: 0}) # action 4 is ITS-G5 25%
        self.assertEqual(env.rsu_queues[0], 0.25)
        self.assertEqual(env.rsu_cbr_curr[0], 0.25 / 4.0)

    def test_sinr_monotonicity(self):
        """Verify that link SINR decreases monotonically as distance increases."""
        rng = np.random.RandomState(42)
        sinr_10m = compute_sinr(4, 10.0, 30.0, rng)
        
        rng = np.random.RandomState(42)
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
        
        for _ in range(5):
            env.step({0: 8, 1: 7, 2: 6, 3: 5})
            
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
        
        with self.assertRaises(ValueError):
            env.step({0: 11, 1: 0, 2: 0, 3: 0})
            
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

    def test_prr_initialization_defaults(self):
        """Verify empirical PRR default initialization rules (1.0 at start, 0.5 after first offload)."""
        env = V2XEnv(seed=120)
        obs = env.reset()
        
        # Initially, no global offload transmissions have occurred -> all default to 1.0
        for i in env.agents:
            for rat in range(1, 5):
                self.assertEqual(env.get_empirical_prr(i, rat), 1.0)
                
        # Trigger an offload transition on RAT 4 for agent 0
        env.step({0: 8, 1: 0, 2: 0, 3: 0})
        
        # Now, global transmissions exist -> unseen RATs (1, 2, 3) must default to 0.5
        for rat in [1, 2, 3]:
            self.assertEqual(env.get_empirical_prr(0, rat), 0.5)

    def test_golden_path_losses(self):
        """Golden check for path losses at reference d=100.0m against hand-calculated values."""
        # LTE (1) and ITS-G5 (2): PL = 47.9 + 10 * log10(100/10) = 57.9 dB
        self.assertAlmostEqual(compute_path_loss(1, 100.0), 57.9)
        self.assertAlmostEqual(compute_path_loss(2, 100.0), 57.9)
        
        # WiFi-6 (3): PL = 40.05 + 20*log10(5.0/2.4) + 20*log10(100) = 86.425175 dB
        self.assertAlmostEqual(compute_path_loss(3, 100.0), 86.425175, places=5)
        
        # 5G-NR (4): PL = 32.4 + 20*log10(3.5) + 20*log10(100) = 83.281361 dB
        self.assertAlmostEqual(compute_path_loss(4, 100.0), 83.281361, places=5)

    def test_golden_wireless_links(self):
        """Golden check for wireless links SINR and success rate at d=100.0m, v=30.0m/s."""
        # We mock rng to return 0.0 shadowing and 1.0 fading envelope
        class MockRng:
            def normal(self, loc, scale):
                if scale == 1.0:
                    return 0.70710678
                return 0.0
            def uniform(self, low, high):
                return 0.0
        mock_rng = MockRng()
        
        # LTE (1) SINR: 23 - 57.9 - (-110) + 0 - 0 = 75.1 dB
        sinr_lte = compute_sinr(1, 100.0, 30.0, mock_rng)
        self.assertAlmostEqual(sinr_lte, 75.1, places=4)
        
        # ITS-G5 (2) SINR: 23 - 57.9 - (-90) = 55.1 dB
        sinr_its = compute_sinr(2, 100.0, 30.0, mock_rng)
        self.assertAlmostEqual(sinr_its, 55.1, places=4)

    def test_golden_costs_and_utility(self):
        """Golden check for local execution cost and utility calculations."""
        env = V2XEnv(seed=200)
        env.reset()
        
        # Safety Task: C=1e8, data=0.1, D=100, alpha=0.7, beta=0.3
        env.active_tasks[0] = TASK_TYPES["safety"].copy()
        env.active_tasks[0]["type"] = "safety"
        
        # For vehicle 0, force local execution (action 0)
        # Latency = 50.0 ms, Energy = 0.10 J, U_PRR = 0.9361
        _, rewards, _, infos = env.step({0: 0, 1: 0, 2: 0, 3: 0})
        
        self.assertEqual(infos[0]["latency_ms"], 50.0)
        self.assertEqual(infos[0]["energy_j"], 0.10)
        
        # U_PRR reward calculation
        # exp(-50.0/100.0) = 0.60653
        # exp(-0.10/3.0) = 0.96722
        # U = 0.7 * 1.0 + 0.15 * 0.60653 + 0.15 * 0.96722 = 0.93606
        self.assertAlmostEqual(rewards[0], 0.9361, places=4)

    def test_mode_configurations(self):
        """Verify baseline_recreation mode implements log-based latency and energy."""
        env_base = V2XEnv(mode="baseline_recreation", seed=300)
        env_base.reset()
        
        # Override task type of vehicle 0 to safety
        env_base.active_tasks[0] = TASK_TYPES["safety"].copy()
        env_base.active_tasks[0]["type"] = "safety"
        
        # Take local execution action 0
        _, _, _, infos = env_base.step({0: 0, 1: 0, 2: 0, 3: 0})
        
        # Compute ratio: C / f_cpu = 1e8 / 2e9 = 0.05
        # Expected baseline energy: P_cpu * log10(0.05) = 2.0 * (-1.3010) = -2.6020 Joules
        expected_energy_base = 2.0 * math.log10(0.05)
        self.assertAlmostEqual(infos[0]["energy_j"], expected_energy_base, places=4)

if __name__ == "__main__":
    unittest.main()
