import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env.environment import V2XEnv

class TestEnergyModes(unittest.TestCase):
    
    def test_legacy_mode_no_conversion(self):
        # Action 8 is 5G AllOffload, task type compute
        env = V2XEnv(n_vehicles=1, seed=42, mode="physically_corrected", policy_type="alloffload", energy_mode="energy_legacy_unconverted")
        env.reset()
        env.active_tasks[0] = {
            "type": "compute",
            "D_ms": 1000.0,
            "data_mb": 5.0,
            "cpu_cycles": 2e9,
            "alpha": 0.20,
            "beta": 0.80
        }
        
        # Take Action 8 (5G 100%)
        action_dict = {0: 8}
        next_obs, rews, dones, infos = env.step(action_dict)
        
        # Under legacy, e_tx = 0.8 * 5.0 = 4.0 Joules
        # Because local cpu energy is 0.0 when rho=1.0, total energy should be exactly 4.0
        self.assertAlmostEqual(infos[0]["energy_j"], 4.0, places=4)
        
    def test_si_corrected_conversion(self):
        env = V2XEnv(n_vehicles=1, seed=42, mode="physically_corrected", policy_type="alloffload", energy_mode="energy_si_corrected")
        env.reset()
        env.active_tasks[0] = {
            "type": "compute",
            "D_ms": 1000.0,
            "data_mb": 5.0,
            "cpu_cycles": 2e9,
            "alpha": 0.20,
            "beta": 0.80
        }
        
        # Take Action 8 (5G 100%)
        action_dict = {0: 8}
        next_obs, rews, dones, infos = env.step(action_dict)
        
        # Under SI corrected, e_tx = (0.8 * 5.0) / 1000.0 = 0.004 Joules
        self.assertAlmostEqual(infos[0]["energy_j"], 0.004, places=4)
        
    def test_non_negative_energy(self):
        env = V2XEnv(n_vehicles=10, seed=42, energy_mode="energy_si_corrected")
        env.reset()
        for action in range(11):
            action_dict = {i: action for i in range(10)}
            next_obs, rews, dones, infos = env.step(action_dict)
            for i in range(10):
                self.assertGreaterEqual(infos[i]["energy_j"], 0.0)

if __name__ == "__main__":
    unittest.main()
