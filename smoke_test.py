import os
import sys

# Add src/maro_pe path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/maro_pe')))

from maro_pe.env.ns3_sumo_env import Ns3SumoV2XEnv

def main():
    print("Starting Ns3SumoV2XEnv initialization...")
    env = Ns3SumoV2XEnv(start_sim=False, n_vehicles=16)
    
    print("Resetting environment...")
    obs = env.reset()
    print(f"Observation length: {len(obs)}")
    
    print("Stepping environment...")
    action = {i: 0 for i in env.agents}
        
    obs, reward, done, info = env.step(action)
    print("Step successful!")

if __name__ == "__main__":
    main()
