import unittest
import numpy as np
import sys
sys.path.append('.')

from env.environment_plus import V2XEnvPlus

class TestRewardBackwardCompatibility(unittest.TestCase):
    def test_default_parameterization_matches_frozen_baseline(self):
        # Instantiate frozen-style hardcoded env
        env_base = V2XEnvPlus(seed=42)
        env_base.reward_type = "linear"
        env_base.w_s = 0.4
        env_base.w_t = 0.3
        env_base.w_e = 0.2
        env_base.w_q = 0.05
        env_base.w_o = 0.05
        
        # Instantiate parameterized env with defaults
        env_param = V2XEnvPlus(seed=42)
        
        # Manually construct state to force different SLA outcomes
        # Case 1: Uncongested
        env_base.reset(seed=42)
        env_param.reset(seed=42)
        
        # Sync states
        for env in [env_base, env_param]:
            env.Q_t = 0
            env.vehicles[0]["gamma_5g"] = 1000
            env.active_tasks[0] = {"class": 3, "D": 1.0, "B": 50*8*1024, "L": 15e6}
            
        _, r_base, _, _ = env_base.step({0: 10}) # 100% 5G
        _, r_param, _, _ = env_param.step({0: 10})
        
        self.assertAlmostEqual(r_base[0], r_param[0], places=6, msg="Reward mismatch on successful task")
        
        # Case 2: Congested SLA Violation
        for env in [env_base, env_param]:
            env.reset(seed=42)
            env.Q_t = 100e6
            env.vehicles[0]["gamma_5g"] = 1000
            env.active_tasks[0] = {"class": 1, "D": 0.1, "B": 2400, "L": 1e6}
            
        _, r_base, _, _ = env_base.step({0: 10})
        _, r_param, _, _ = env_param.step({0: 10})
        
        self.assertAlmostEqual(r_base[0], r_param[0], places=6, msg="Reward mismatch on SLA violation")
        
        # Case 3: Inactive task
        for env in [env_base, env_param]:
            env.reset(seed=42)
            env.active_tasks = {} # Clear tasks
            
        _, r_base, _, _ = env_base.step({0: 10})
        _, r_param, _, _ = env_param.step({0: 10})
        
        self.assertAlmostEqual(r_base.get(0, 0.0), 0.0, places=6, msg="Inactive task must have 0 reward")
        self.assertAlmostEqual(r_param.get(0, 0.0), 0.0, places=6, msg="Inactive task must have 0 reward")

if __name__ == '__main__':
    unittest.main()
