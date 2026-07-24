import torch
import numpy as np
import pandas as pd
import sys
sys.path.append('.')

from agents.d3qn.agent import D3QNAgent
from env.environment_plus import V2XEnvPlus

def run_trajectory_q_evaluation():
    seeds = [111, 222, 333]
    task_probs = [0.3, 0.5, 0.7, 0.9, 1.0]
    episodes = 20
    
    records = []
    
    for seed in seeds:
        print(f"Loading agents for Seed {seed}...")
        ckpt_dir = f"checkpoints_b33b/fedavg_Candidate_B_seed_{seed}"
        agents = []
        for i in range(16):
            agent = D3QNAgent(state_dim=20, action_dim=11, seed=seed)
            agent.online_net.load_state_dict(torch.load(f"{ckpt_dir}/agent_{i}.pt", map_location="cpu"))
            agent.online_net.eval()
            agents.append(agent)
            
        for p_task in task_probs:
            print(f"  Evaluating p_task = {p_task}...")
            env = V2XEnvPlus(n_vehicles=16, seed=seed, f_mec=0.316e9, bg_workload_enabled=True,
                             w_s=0.0, w_t=0.0, w_e=0.0, reward_type="piecewise")
            env.task_prob = p_task
            
            for ep in range(episodes):
                obs = env.reset(seed=seed + ep)
                done = False
                while not done:
                    actions = {}
                    for i in range(16):
                        q_val = obs[i][1] * env.Q_max
                        
                        with torch.no_grad():
                            device = next(agents[i].online_net.parameters()).device
                            state_tensor = torch.FloatTensor(obs[i]).unsqueeze(0).to(device)
                            q_values = agents[i].online_net(state_tensor).cpu().numpy()[0]
                            
                            act = np.argmax(q_values)
                            actions[i] = act
                            
                            # Calculate family Q values
                            q_local = q_values[0]
                            q_lte_max = np.max(q_values[1:6])
                            q_5g_max = np.max(q_values[6:11])
                            
                            records.append({
                                "Seed": seed,
                                "p_task": p_task,
                                "Episode": ep,
                                "ClientIdx": i,
                                "Queue": q_val,
                                "Q_Local": q_local,
                                "Q_LTE_max": q_lte_max,
                                "Q_5G_max": q_5g_max,
                                "Argmax_Action": act,
                                "DeltaQ_5G_Loc": q_5g_max - q_local,
                                "Local_beats_5G": q_local > q_5g_max,
                                "Local_is_Argmax": (act == 0),
                                "LTE_beats_5G": q_lte_max > q_5g_max
                            })
                            
                    obs, _, done_dict, _ = env.step(actions)
                    done = done_dict["__all__"]
                    
    df = pd.DataFrame(records)
    df.to_csv("analysis/B33F_TRAJECTORY_Q_VALUES.csv", index=False)
    print("Saved trajectory Q-values to analysis/B33F_TRAJECTORY_Q_VALUES.csv")

if __name__ == "__main__":
    run_trajectory_q_evaluation()
