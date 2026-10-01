import sys
import numpy as np
import torch
from env.environment import V2XEnv
from env.config import TASK_TYPES
from agents.d3qn.agent import D3QNAgent

def main():
    n_vehicles = 8
    seed = 2 # paper uses seed=2
    env = V2XEnv(n_vehicles=n_vehicles, seed=seed, mode="physically_corrected")
    
    ckpt_path = f"_claude_workspace/results/CAMPAIGN_PHYSICS_FIX_20260818/raw/n8/ma-rope_seed{seed}.pt"
    
    # Setup agents
    agents = {i: D3QNAgent(state_dim=12, action_dim=11, seed=seed+i) for i in range(n_vehicles)}
    print(f"Loading {ckpt_path}...")
    full_state_dict = torch.load(ckpt_path, weights_only=False)
    agent_state_dicts = full_state_dict["all_agent_online_net_state_dicts"]
    
    for idx, agent in agents.items():
        agent.online_net.load_state_dict(agent_state_dicts[idx])
        agent.target_net.load_state_dict(agent_state_dicts[idx])

    task_stats = {
        "safety": {"tx": 0, "success": 0, "on_time": 0, "latencies": []},
        "infotainment": {"tx": 0, "success": 0, "on_time": 0, "latencies": []},
        "compute": {"tx": 0, "success": 0, "on_time": 0, "latencies": []}
    }

    print("Running 100 episodes...")
    for ep in range(100):
        obs = env.reset()
        done = False
        while not done:
            action_dict = {}
            for i in range(n_vehicles):
                action_dict[i] = agents[i].select_action(obs[i], is_safety_task=(env.active_tasks[i]["type"] == "safety"), evaluate=True)
            
            obs_next, rewards, dones, infos = env.step(action_dict)
            done = dones.get("__all__", False)
            
            for i in range(n_vehicles):
                info = infos[i]
                if "task_type" in info:
                    ttype = info["task_type"]
                    rat = info.get("chosen_rat", 0)
                    rho = info.get("adapted_rho", 0.0)
                    
                    if rat > 0 and rho > 0.0:
                        lat = info["latency_ms"]
                        task_stats[ttype]["tx"] += 1
                        if info["transmission_success"]:
                            task_stats[ttype]["success"] += 1
                            task_stats[ttype]["latencies"].append(lat)
                            if lat <= TASK_TYPES[ttype]["D_ms"]:
                                task_stats[ttype]["on_time"] += 1
                                
            obs = obs_next

    for ttype, stats in task_stats.items():
        otr = stats['on_time'] / max(1, stats['tx'])
        prr = stats['success'] / max(1, stats['tx'])
        mean_lat = np.mean(stats['latencies']) if stats['latencies'] else 0.0
        print(f"{ttype} | tx: {stats['tx']} | OTR: {otr:.4f} | PRR: {prr:.4f} | Lat: {mean_lat:.2f}")

if __name__ == "__main__":
    main()
