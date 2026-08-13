import numpy as np
import math

class Approx:
    def __init__(self, expected, rel=1e-6, abs=1e-12):
        self.expected = expected
        self.rel = rel
        self.abs = abs

    def __eq__(self, actual):
        return math.isclose(actual, self.expected, rel_tol=self.rel, abs_tol=self.abs)

class PytestMock:
    approx = Approx

pytest = PytestMock()
from env.environment_plus import V2XEnvPlus
from tests.test_marope_plus_math import (
    calc_total_latency, calc_total_energy, calc_queue_latency
)

def test_reward_bounds():
    env = V2XEnvPlus(n_vehicles=10)
    env.reset(seed=42)
    
    actions = {i: np.random.randint(0, 11) for i in range(10)}
    _, rewards, _, _ = env.step(actions)
    
    min_bound = -env.w_q - env.w_o
    max_bound = 1.0
    
    for r in rewards.values():
        assert min_bound <= r <= max_bound, f"Reward {r} out of bounds [{min_bound}, {max_bound}]"

def test_env_matches_golden_math():
    env = V2XEnvPlus(n_vehicles=1)
    env.reset(seed=42)
    
    # Force the queue state
    env.Q_t = 1e7
    
    # Force the task to match the golden test parameters (Safety, rho=0.5)
    env.active_tasks = {0: {"class": 1, "D": 0.1, "B": 2400, "L": 1e6}}
    
    # Force action 2 -> (LTE, 0.4) wait, I need rho=0.5 but our discrete space doesn't have 0.5.
    # We defined {0.2, 0.4, 0.6, 0.8, 1.0}. Let's test rho=0.4
    rho = 0.4
    
    actions = {0: 2} # Action 2 is LTE, rho=0.4
    
    # To compare with golden math, we must force tx_success = True
    class MockRNG:
        def uniform(self, *args, **kwargs):
            return 0.0
    env.np_random = MockRNG() # Force p_radio > 0.0 to succeed
    
    _, _, _, infos = env.step(actions)
    
    info = infos[0]
    
    # Calculate golden math for rho = 0.4
    golden_t = calc_total_latency(rho, 1e6, 2400, env.f_local, env.f_mec, env.R_lte, 1e7)
    golden_e = calc_total_energy(rho, 1e6, 2400, env.f_local, env.R_lte, env.P_tx_lte, env.kappa_cpu)
    
    assert info["T_i"] == pytest.approx(golden_t)
    assert info["E_i"] == pytest.approx(golden_e)

def test_deterministic_trajectory():
    # Same seed should produce identical trajectories
    env1 = V2XEnvPlus(n_vehicles=5, seed=42)
    obs1 = env1.reset()
    
    env2 = V2XEnvPlus(n_vehicles=5, seed=42)
    obs2 = env2.reset()
    
    # Check initial observations
    for k in obs1:
        np.testing.assert_array_almost_equal(obs1[k], obs2[k])
        
    # Step with identical actions
    actions = {0: 1, 1: 3, 2: 7, 3: 0, 4: 10}
    
    _, r1, _, i1 = env1.step(actions)
    _, r2, _, i2 = env2.step(actions)
    
    for k in r1:
        assert r1[k] == r2[k]
        assert i1[k]["T_i"] == i2[k]["T_i"]
        assert i1[k]["S_i"] == i2[k]["S_i"]

if __name__ == "__main__":
    test_reward_bounds()
    test_env_matches_golden_math()
    test_deterministic_trajectory()
    print("V2XEnvPlus verification tests passed!")
