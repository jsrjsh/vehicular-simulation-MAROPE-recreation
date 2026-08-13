import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env.environment import V2XEnv

class TestQueueModes(unittest.TestCase):
    def test_queue_accumulation_differences(self):
        env_legacy = V2XEnv(n_vehicles=32, mode="legacy_guide", policy_type="alloffload")
        env_manuscript = V2XEnv(n_vehicles=32, mode="manuscript_calibrated", policy_type="alloffload")
        
        # Reset with same seed
        env_legacy.reset(seed=100)
        env_manuscript.reset(seed=100)
        
        # Step once with alloffload (step 1: all tasks are 'new' from reset)
        actions = {i: 8 for i in range(32)}
        env_legacy.step(actions)
        env_manuscript.step(actions)
        
        # Step again (step 2: now task resampling occurs with 0.3 prob)
        _, _, _, infos_legacy = env_legacy.step(actions)
        _, _, _, infos_manuscript = env_manuscript.step(actions)
        
        # We can extract the queue delay from infos
        # Since queue delay = queue size * DELAY_PER_UNIT_MS
        # For legacy: size=32, scalar=50, delay per RSU could be 32/n_rsus * 50
        # For manuscript: size=~10, scalar=35
        
        avg_q_legacy = sum(infos_legacy[i]["queue_delay_ms"] for i in range(32)) / 32
        avg_q_manuscript = sum(infos_manuscript[i]["queue_delay_ms"] for i in range(32)) / 32
        
        # legacy queue delay should be significantly larger
        self.assertGreater(avg_q_legacy, avg_q_manuscript, "Legacy guide mode should accumulate a higher queue depth (and delay).")
        
        # Check actual queue depths by inspecting env variables
        legacy_q_sum = sum(env_legacy.rsu_queues.values())
        manuscript_q_sum = sum(env_manuscript.rsu_queues.values())
        
        # 32 vehicles offloading in legacy vs only active in manuscript
        self.assertGreater(legacy_q_sum, manuscript_q_sum, "Legacy should queue more vehicles than manuscript.")
        self.assertEqual(legacy_q_sum, 32.0, "Legacy should queue all 32 vehicles.")
        self.assertLess(manuscript_q_sum, 32.0, "Manuscript should only queue active vehicles.")

if __name__ == "__main__":
    unittest.main()
