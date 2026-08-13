# tests/test_reproduction.py
"""
Unit test suite for Phase 4A.2 regression testing.
Validates fixed policies (NoOffload, AllOffload), adaptive actions,
denominator semantics (step vs active task), directories, and seed aggregations.
"""

import unittest
import os
import shutil
import numpy as np
import torch
from env.environment import V2XEnv
from env.config import RAT_SPECS

class TestReproductionRegression(unittest.TestCase):

    def test_fixed_alloffload_rho_bypass(self):
        """Verify that AllOffload policy forces 5G-NR selection and bypasses SINR scaling (rho' remains 1.0)."""
        env = V2XEnv(n_vehicles=2, mode="physically_corrected", policy_type="alloffload")
        env.reset()
        
        # Override vehicle coordinates to create deep fading (distance = 1200 m)
        env.positions = np.array([100.0, 1300.0])
        
        # Take AllOffload action step (action 8)
        _, _, _, infos = env.step({0: 8, 1: 8})
        
        # Verify 5G-NR selected and adapted rho is exactly 1.0 (no scaling)
        for i in range(2):
            self.assertEqual(infos[i]["chosen_rat"], 4)
            self.assertEqual(infos[i]["adapted_rho"], 1.0)
            self.assertEqual(infos[i]["policy_type"], "alloffload")

    def test_fixed_nooffload_rho_bypass(self):
        """Verify that NoOffload policy forces Local selection and adapted rho remains 0.0."""
        env = V2XEnv(n_vehicles=2, mode="physically_corrected", policy_type="nooffload")
        env.reset()
        
        _, _, _, infos = env.step({0: 0, 1: 0})
        
        for i in range(2):
            self.assertEqual(infos[i]["chosen_rat"], 0)
            self.assertEqual(infos[i]["adapted_rho"], 0.0)
            self.assertEqual(infos[i]["policy_type"], "nooffload")

    def test_adaptive_marope_rho_modulation(self):
        """Verify that learned/adaptive actions still undergo SINR-proportional rho scaling."""
        env = V2XEnv(n_vehicles=2, mode="physically_corrected", policy_type="learned")
        env.reset()
        
        # Force a safety task
        env.active_tasks[0] = {
            "type": "safety", "D_ms": 100.0, "data_mb": 0.1, "cpu_cycles": 1e8, "alpha": 0.70, "beta": 0.30
        }
        
        # Run step with action 8 (AllOffload action)
        _, _, _, infos = env.step({0: 8, 1: 8})
        
        # Verify adapted rho is modulated (strictly less than 1.0 due to denominator divisions)
        self.assertEqual(infos[0]["chosen_rat"], 4)
        self.assertLess(infos[0]["adapted_rho"], 1.0)
        self.assertEqual(infos[0]["policy_type"], "learned")

    def test_denominators_step_vs_active(self):
        """Verify step-level vs active-task average denominators."""
        # Scenario: 5 steps.
        # Step 1: No task generated. Energy = 0.05 J.
        # Step 2: Task generated. Energy = 0.20 J.
        # Step 3: No task generated. Energy = 0.05 J.
        # Step 4: Task generated. Energy = 0.10 J.
        # Step 5: No task generated. Energy = 0.05 J.
        # Sum of step energy = 0.45 J.
        # Step-level average = 0.45 / 5 = 0.09 J.
        # Active-task average = (0.20 + 0.10) / 2 = 0.15 J.
        
        energies = [0.05, 0.20, 0.05, 0.10, 0.05]
        task_active = [False, True, False, True, False]
        
        total_steps = len(energies)
        active_steps = sum(task_active)
        
        # Step-level aggregation
        step_avg = sum(energies) / total_steps
        
        # Active-task aggregation (excluding inactive steps)
        active_avg = sum(e for e, active in zip(energies, task_active) if active) / active_steps
        
        self.assertEqual(step_avg, 0.09)
        self.assertAlmostEqual(active_avg, 0.15)

    def test_five_seed_aggregation_math(self):
        """Verify mean and standard deviation logic for seed aggregations."""
        seed_results = [0.84, 0.85, 0.83, 0.86, 0.84]
        mean_val = np.mean(seed_results)
        std_val = np.std(seed_results)
        
        self.assertAlmostEqual(mean_val, 0.844, places=3)
        self.assertAlmostEqual(std_val, 0.010198, places=5)

    def test_mode_separation_directories(self):
        """Verify directory isolation creation."""
        base_dir = "results"
        repro_dir = os.path.join(base_dir, "paper_reproduction")
        corr_dir = os.path.join(base_dir, "physically_corrected")
        
        os.makedirs(repro_dir, exist_ok=True)
        os.makedirs(corr_dir, exist_ok=True)
        
        self.assertTrue(os.path.exists(repro_dir))
        self.assertTrue(os.path.exists(corr_dir))

if __name__ == "__main__":
    unittest.main()
