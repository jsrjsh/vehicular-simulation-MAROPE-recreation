"""Data for the regenerated queue-contention figure (reviewer response, 2026-10-14).
k vehicles share ONE RSU. Corrected simulator (campaign code in ../_claude_workspace, mode baseline_recreation + the three fixes).
Per (k, seed): AllOffload with the queue model on and off, NoOffload, and MA-ROPE trained for 100 episodes (queue on),
evaluated on 10 held-out episodes (eps = 0.05 as in the paper's protocol). Metric: mean reward U_PRR over all vehicle-steps."""
import json, os, sys, time
import numpy as np, torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_claude_workspace"))
from env.environment import V2XEnv
from agents.federated.coordinator import FederatedCoordinator
torch.set_num_threads(1)
k, seed = int(sys.argv[1]), int(sys.argv[2])
RSU = [1300.0]
def mk(policy, queue, s):
    return V2XEnv(n_vehicles=k, rsu_positions=RSU, scenario="urllc", max_steps=100, seed=s, mode="baseline_recreation",
                  policy_type=policy, include_rsu_queue=queue)
eval_seeds = [1_000_000 + 1000 * seed + e for e in range(1, 11)]
def run(env, act_fn):
    u = []
    for es in eval_seeds:
        obs = env.reset(seed=es); done = False
        while not done:
            obs, r, d, _ = env.step({i: act_fn(i, obs[i], env) for i in range(k)}); done = d[0]; u += [r[i] for i in range(k)]
    return float(np.mean(u))
res = {"k": k, "seed": seed}
res["alloffload_queue_off"] = run(mk("alloffload", False, seed), lambda i, o, e: 8)
res["alloffload_queue_on"] = run(mk("alloffload", True, seed), lambda i, o, e: 8)
res["nooffload"] = run(mk("nooffload", True, seed), lambda i, o, e: 0)
t0 = time.time()
env = mk("learned", True, seed)
coord = FederatedCoordinator(n_agents=k, state_dim=12, action_dim=11, buffer_capacity=5000, batch_size=32,
                             target_update_frequency=100, replay_mode="prioritized", participation_prob=0.9, seed=seed)
steps = 0
for ep in range(100):
    obs = env.reset(); done = False
    while not done:
        act = {i: coord.agents[i].select_action(obs[i], is_safety_task=(env.active_tasks[i]["type"] == "safety")) for i in range(k)}
        nobs, rew, dones, _ = env.step(act); done = dones[0]; steps += 1
        for i in range(k):
            coord.agents[i].replay_buffer.add(obs[i], act[i], rew[i], nobs[i], dones[i]); coord.agents[i].learn()
        obs = nobs
        if steps % 50 == 0: coord.aggregate_and_broadcast()
res["maprope"] = run(mk("learned", True, seed), lambda i, o, e: coord.agents[i].select_action(o, is_safety_task=(e.active_tasks[i]["type"] == "safety"), evaluate=True))
res["train_seconds"] = round(time.time() - t0, 1)
os.makedirs(os.path.join(HERE, "results_fig9"), exist_ok=True)
json.dump(res, open(os.path.join(HERE, "results_fig9", f"k{k}_seed{seed}.json"), "w"))
print(k, seed, {a: round(b, 3) for a, b in res.items() if isinstance(b, float)})
