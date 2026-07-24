import torch
import numpy as np
import pandas as pd
import sys
sys.path.append('.')

from agents.d3qn.agent import D3QNAgent
from env.environment_plus import V2XEnvPlus

def evaluate_matched_outcomes():
    seeds = [111, 222, 333]
    task_probs = [0.3, 0.5, 0.7, 0.9, 1.0]
    episodes = 20
    
    results = []
    
    for seed in seeds:
        print(f"Evaluating Seed {seed}...")
        ckpt_dir = f"checkpoints_b33b/fedavg_Candidate_B_seed_{seed}"
        agents = []
        for i in range(16):
            agent = D3QNAgent(state_dim=20, action_dim=11, seed=seed)
            agent.online_net.load_state_dict(torch.load(f"{ckpt_dir}/agent_{i}.pt", map_location="cpu"))
            agent.online_net.eval()
            agents.append(agent)
            
        for p_task in task_probs:
            env = V2XEnvPlus(n_vehicles=16, seed=seed, f_mec=0.316e9, bg_workload_enabled=True,
                             w_s=0.0, w_t=0.0, w_e=0.0, reward_type="piecewise")
            env.task_prob = p_task
            
            queue_history = []
            latency_history = []
            sla_successes = 0
            total_tasks = 0
            local_actions = 0
            total_actions = 0
            
            for ep in range(episodes):
                obs = env.reset(seed=seed + ep)
                done = False
                while not done:
                    actions = {}
                    for i in range(16):
                        # Pre-decision queue
                        q_val = obs[i][1] * env.Q_max
                        queue_history.append(q_val)
                        
                        with torch.no_grad():
                            device = next(agents[i].online_net.parameters()).device
                            state_tensor = torch.FloatTensor(obs[i]).unsqueeze(0).to(device)
                            q_values = agents[i].online_net(state_tensor).cpu().numpy()[0]
                            act = np.argmax(q_values)
                            actions[i] = act
                            if act == 0:
                                local_actions += 1
                            total_actions += 1
                            
                    obs, rewards, done_dict, infos = env.step(actions)
                    done = done_dict["__all__"]
                    
                    for i in range(16):
                        if "T_i" in infos[i]:
                            t_i = infos[i]["T_i"]
                            s_i = infos[i]["S_i"]
                            latency_history.append(t_i)
                            total_tasks += 1
                            if s_i > 0:
                                sla_successes += 1
                                
            res = {
                "Seed": seed,
                "p_task": p_task,
                "Local_Freq": local_actions / total_actions if total_actions > 0 else 0,
                "Mean_Queue": np.mean(queue_history),
                "p95_Queue": np.percentile(queue_history, 95),
                "SLA_Success": sla_successes / total_tasks if total_tasks > 0 else 0,
                "Mean_Latency": np.mean(latency_history),
                "p95_Latency": np.percentile(latency_history, 95)
            }
            results.append(res)
            print(f"  p_task={p_task} | Local {res['Local_Freq']*100:.1f}% | SLA {res['SLA_Success']*100:.1f}% | p95 Queue {res['p95_Queue']/1e6:.1f}M")
            
    df = pd.DataFrame(results)
    df.to_csv("analysis/B33F_MATCHED_OUTCOMES.csv", index=False)
    print("\nMatched outcomes saved to analysis/B33F_MATCHED_OUTCOMES.csv")
    
if __name__ == "__main__":
    evaluate_matched_outcomes()
