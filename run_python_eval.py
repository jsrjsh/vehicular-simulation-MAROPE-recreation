import os
import torch
import numpy as np
import sys
from env.environment import V2XEnv
from agents.federated.coordinator import FederatedCoordinator

N = 16
seed = 0

env = V2XEnv(n_vehicles=N, seed=seed, mode="manuscript_calibrated", policy_type="learned", energy_mode="energy_legacy_unconverted", local_reliability_mode="local_success")
coord = FederatedCoordinator(n_agents=N, state_dim=12, action_dim=11, buffer_capacity=5000, batch_size=32, target_update_frequency=100, replay_mode="prioritized", participation_prob=0.9, seed=seed)

chkpt_path = f"_claude_workspace/results/CAMPAIGN_LATENCY_FIX_20260815/raw/n{N}/ma-rope_seed{seed}.pt"
coord.global_network.load_state_dict(torch.load(chkpt_path, map_location="cpu"))
coord.sync_all_agents()

fleet_otrs = []
prrs = []
u_otrs = []

for ep in range(5):
    obs = env.reset()
    ep_u = []
    ep_tx = 0
    ep_success = 0
    ep_on_time = 0
    
    for step in range(100):
        actions = coord.select_actions(obs, evaluate=True)
        next_obs, rewards, dones, infos = env.step(actions)
        obs = next_obs
        
        for i in range(N):
            ep_u.append(infos[i]["u_otr"])
            rat = infos[i]["chosen_rat"]
            if rat > 0:
                ep_tx += 1
                if infos[i]["transmission_success"]:
                    ep_success += 1
                    if infos[i]["latency_ms"] <= env.active_tasks[i]["D_ms"]:
                        ep_on_time += 1
                        
    fleet_otrs.append(ep_on_time / max(1, ep_tx))
    prrs.append(ep_success / max(1, ep_tx))
    u_otrs.append(np.mean(ep_u))
    
print(f"Mean Fleet OTR: {np.mean(fleet_otrs):.4f}")
print(f"Mean PRR: {np.mean(prrs):.4f}")
print(f"Mean u_otr_active: {np.mean(u_otrs):.4f}")
