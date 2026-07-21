import json
import torch
import numpy as np
from env.environment_plus import V2XEnvPlus
from agents.federated.coordinator_plus import FederatedCoordinatorPlus

def run_smoke_test():
    print("Starting MA-ROPE+ Phase B Smoke Test...")
    n_vehicles = 4
    
    # Initialize env
    env = V2XEnvPlus(n_vehicles=n_vehicles, max_steps=5, seed=42)
    obs = env.reset()
    
    # Initialize coordinator
    coord = FederatedCoordinatorPlus(n_agents=n_vehicles, theta_round=0.5)
    
    # Mock dummy neural network states for clients
    def make_model(val):
        return {
            "fc1.weight": torch.full((10, 10), val, dtype=torch.float32),
            "batches": torch.tensor(100, dtype=torch.long)
        }
    
    client_models = {i: make_model(float(i + 1)) for i in range(n_vehicles)}
    
    for step in range(5):
        # Step env with deterministic actions
        actions = {i: (i % 11) for i in range(n_vehicles)}
        obs, rewards, dones, infos = env.step(actions)
        
        # In a real setup, local training happens here.
        # We will just pass the dummy client models and the infos to the coordinator
        global_model, report = coord.aggregate_and_broadcast(client_models, infos)
        
        print(f"--- Step {step} ---")
        print(json.dumps(report, indent=2))
        
        if report["round_executed"]:
            print("Global Model weight sample:", global_model["fc1.weight"][0,0].item())
            
        # Update client models with global model
        if global_model is not None:
            for i in range(n_vehicles):
                client_models[i] = global_model
                
    print("Smoke test completed successfully!")

if __name__ == "__main__":
    run_smoke_test()
