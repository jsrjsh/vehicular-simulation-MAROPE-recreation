import torch
import math

class PytestRaises:
    def __init__(self, exc_type, match=None):
        self.exc_type = exc_type
        self.match = match
        
    def __enter__(self):
        pass
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"DID NOT RAISE {self.exc_type}")
        if not issubclass(exc_type, self.exc_type):
            return False
        if self.match and self.match not in str(exc_val):
            raise AssertionError(f"Pattern '{self.match}' not found in '{str(exc_val)}'")
        return True

class PytestMock:
    raises = PytestRaises

pytest = PytestMock()
from agents.federated.coordinator_plus import FederatedCoordinatorPlus

def get_dummy_model(val_float, val_int):
    return {
        "layer1.weight": torch.full((2, 2), val_float, dtype=torch.float32),
        "layer1.bias": torch.full((2,), val_float, dtype=torch.float32),
        "num_batches_tracked": torch.tensor(val_int, dtype=torch.long)
    }

def test_equal_sample_counts():
    coord = FederatedCoordinatorPlus(n_agents=2, theta_round=0.0)
    
    agent_models = {
        0: get_dummy_model(1.0, 10),
        1: get_dummy_model(3.0, 20)
    }
    
    infos = {
        0: {"battery_j": 200, "uplink_sinr": 5.0, "local_sample_count": 50},
        1: {"battery_j": 200, "uplink_sinr": 5.0, "local_sample_count": 50}
    }
    
    global_model, report = coord.aggregate_and_broadcast(agent_models, infos)
    
    assert report["round_executed"]
    assert len(report["eligible_clients"]) == 2
    # Expect average of 1.0 and 3.0 = 2.0
    assert torch.allclose(global_model["layer1.weight"], torch.full((2, 2), 2.0))
    # Expect integer buffer to take first eligible client's value (10)
    assert global_model["num_batches_tracked"].item() == 10

def test_unequal_sample_counts():
    coord = FederatedCoordinatorPlus(n_agents=2, theta_round=0.0)
    
    agent_models = {
        0: get_dummy_model(1.0, 10),
        1: get_dummy_model(3.0, 20)
    }
    
    infos = {
        0: {"battery_j": 200, "uplink_sinr": 5.0, "local_sample_count": 10},
        1: {"battery_j": 200, "uplink_sinr": 5.0, "local_sample_count": 90}
    }
    
    global_model, report = coord.aggregate_and_broadcast(agent_models, infos)
    
    assert report["round_executed"]
    # Expect weighted average: (10*1.0 + 90*3.0) / 100 = 2.8
    assert torch.allclose(global_model["layer1.weight"], torch.full((2, 2), 2.8))

def test_zero_clients():
    coord = FederatedCoordinatorPlus(n_agents=2, theta_round=0.0)
    
    agent_models = {0: get_dummy_model(1.0, 10), 1: get_dummy_model(1.0, 10)}
    
    infos = {
        0: {"battery_j": 50, "uplink_sinr": 5.0, "local_sample_count": 10}, # Battery too low (default 100)
        1: {"battery_j": 200, "uplink_sinr": 0.5, "local_sample_count": 10} # SINR too low (default 1.0)
    }
    
    global_model, report = coord.aggregate_and_broadcast(agent_models, infos)
    
    assert not report["round_executed"]
    assert len(report["eligible_clients"]) == 0
    assert "battery" in report["ineligible_reasons"][0]
    assert "sinr" in report["ineligible_reasons"][1]
    assert global_model is None

def test_thresholds():
    coord = FederatedCoordinatorPlus(n_agents=4, theta_round=0.75)
    
    agent_models = {i: get_dummy_model(1.0, 10) for i in range(4)}
    infos = {i: {"battery_j": 200, "uplink_sinr": 5.0, "local_sample_count": 50} for i in range(4)}
    
    # 2/4 = 50% eligible (Below)
    infos[0]["battery_j"] = 0
    infos[1]["battery_j"] = 0
    _, report1 = coord.aggregate_and_broadcast(agent_models, infos)
    assert not report1["round_executed"]
    
    # 3/4 = 75% eligible (Exactly at threshold)
    infos[1]["battery_j"] = 200
    _, report2 = coord.aggregate_and_broadcast(agent_models, infos)
    assert report2["round_executed"]
    
    # 4/4 = 100% eligible (Above)
    infos[0]["battery_j"] = 200
    _, report3 = coord.aggregate_and_broadcast(agent_models, infos)
    assert report3["round_executed"]

def test_mismatches():
    coord = FederatedCoordinatorPlus(n_agents=2, theta_round=0.0)
    infos = {
        0: {"battery_j": 200, "uplink_sinr": 5.0, "local_sample_count": 50},
        1: {"battery_j": 200, "uplink_sinr": 5.0, "local_sample_count": 50}
    }
    
    # Key Mismatch
    m1 = get_dummy_model(1.0, 10)
    m2 = get_dummy_model(1.0, 10)
    m2["layer2.weight"] = torch.zeros(1)
    
    with pytest.raises(KeyError):
        coord.aggregate_and_broadcast({0: m1, 1: m2}, infos)
        
    # Shape Mismatch
    m2 = get_dummy_model(1.0, 10)
    m2["layer1.weight"] = torch.zeros((3, 3))
    with pytest.raises(ValueError, match="shape mismatch"):
        coord.aggregate_and_broadcast({0: m1, 1: m2}, infos)
        
    # NaN check
    m2 = get_dummy_model(1.0, 10)
    m2["layer1.weight"][0,0] = float('nan')
    with pytest.raises(ValueError, match="NaN"):
        coord.aggregate_and_broadcast({0: m1, 1: m2}, infos)

if __name__ == "__main__":
    test_equal_sample_counts()
    test_unequal_sample_counts()
    test_zero_clients()
    test_thresholds()
    test_mismatches()
    print("Coordinator tests passed!")
