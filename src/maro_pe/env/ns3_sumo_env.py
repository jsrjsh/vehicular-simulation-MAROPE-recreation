import numpy as np
from typing import Dict, Any, Tuple
import os
import subprocess
import time
import json

class Ns3SumoV2XEnv:
    """
    OpenAI Gym wrapper for the ns-3 + SUMO co-simulation.
    Replaces the deterministic Python simulation with actual network and mobility traces.
    """
    def __init__(self,
                 n_vehicles: int = 16,
                 max_steps: int = 200,
                 sumo_cfg: str = "src/maro_pe/simulation/sumo_scenario/sumo.sumocfg",
                 ns3_script: str = "marope_ns3_script",
                 ns3_port: int = 0,
                 start_sim: bool = True,
                 seed: int = 42):
        self.n_vehicles = n_vehicles
        self.max_steps = max_steps
        self.sumo_cfg = sumo_cfg
        self.ns3_script = ns3_script
        self.ns3_port = ns3_port
        self.start_sim = start_sim
        self.seed = seed

        self.agents = list(range(self.n_vehicles))
        self.episode_step = 0
        self.active_tasks = {i: {"type": "safety"} for i in self.agents}
        self.env = None

        try:
            from ns3gym import ns3env
            self._ns3env_module = ns3env
            self.use_ns3gym = True
        except ImportError:
            self.use_ns3gym = False
            print("[WARN] ns3gym not found. Using mocked OpenGym interface.")
            return

        self._connect(self.seed)

    def _connect(self, seed):
        # ns3gym only accepts simSeed at Ns3Env construction (its own reset()
        # tears down and relaunches the ns-3 process, but reuses whatever
        # simSeed was passed here for the lifetime of that Ns3Env object --
        # see ns3gym/ns3env.py's Ns3ZmqBridge). The C++ side additionally used
        # to ignore --simSeed entirely (fixed 2026-08-18 in
        # marope_ns3_script.cc, now calls RngSeedManager::SetSeed(simSeed)).
        # A value of exactly 0 is also special-cased by ns3gym as "randomize
        # via unseeded numpy" -- callers must not pass 0.
        assert seed != 0, "ns3gym treats simSeed=0 as 'randomize', not 'seed 0' -- pass a nonzero value"
        self.seed = seed
        if self.env is not None:
            self.env.close()

        env_dir = os.path.dirname(os.path.abspath(__file__))
        trace_file_path = os.path.abspath(os.path.join(env_dir, "..", "simulation", "sumo_scenario", "traces", f"ns2mobility_{self.n_vehicles}.tcl"))
        sim_args = {
            "--n_vehicles": self.n_vehicles,
            "--traceFile": trace_file_path
        }
        self.env = self._ns3env_module.Ns3Env(port=self.ns3_port, stepTime=0.1, startSim=int(self.start_sim), simSeed=self.seed, simArgs=sim_args, debug=True)
        print(f"[INFO] Connected to ns-3 OpenGym interface on port {self.ns3_port} (simSeed={self.seed}).")

    def reset(self, seed=None):
        self.episode_step = 0
        if self.use_ns3gym and self.env is not None:
            # ns3gym's own reset() would just tear down and relaunch using
            # the SAME simSeed the Ns3Env was constructed with (see
            # _connect's docstring) -- for genuinely independent episodes, a
            # fresh seed means a fresh ns-3 process. _connect() constructs a
            # brand-new Ns3Env, whose __init__ already fetches the first
            # observation and leaves envDirty=False -- the .reset() call
            # below then just cheaply returns that observation (ns3gym's own
            # `if not self.envDirty: return self.ns3ZmqBridge.get_obs()`
            # fast path) rather than restarting a second time.
            if seed is not None and seed != self.seed:
                self._connect(seed)
            obs_box = self.env.reset()
            # ns3 env returns a flattened array. Reshape it to (N, 12)
            obs_box = np.array(obs_box).reshape(self.n_vehicles, 12)
            obs = {}
            for i in self.agents:
                obs[i] = np.array(obs_box[i], dtype=np.float32)
            return obs

        return {i: np.zeros(12) for i in self.agents}
        
    def step(self, actions: Dict[int, Any]):
        self.episode_step += 1
        
        if self.use_ns3gym and self.env is not None:
            # action is a dict of ints. Convert to list for Box(N,)
            action_list = [float(actions[i]) for i in self.agents]
            obs_box = self.env.step(action_list)
            
            # unpack tuple if ns3gym returns multiple things
            if isinstance(obs_box, tuple) and len(obs_box) == 4:
                obs_box, reward_val, done, info_str = obs_box
            
            obs_box = np.array(obs_box).reshape(self.n_vehicles, 12)
            
            parsed_info = {}
            if info_str and info_str != "{}":
                try:
                    parsed_info = json.loads(info_str)
                except json.JSONDecodeError:
                    pass
            
            obs = {}
            rewards = {}
            infos = {}
            for i in self.agents:
                obs[i] = np.array(obs_box[i], dtype=np.float32)
                i_str = str(i)
                if i_str in parsed_info:
                    infos[i] = parsed_info[i_str]
                    infos[i]["has_task"] = True
                    infos[i]["effective_action"] = actions[i]
                    rewards[i] = infos[i].get("u_otr", -1.0)
                else:
                    rewards[i] = -1.0
                    infos[i] = {"has_task": True, "effective_action": actions[i]}
                
            dones = {i: done for i in self.agents}
            dones["__all__"] = done
            return obs, rewards, dones, infos
            
        # Mock observations
        obs = {i: np.zeros(12) for i in self.agents}
        rewards = {i: -1.0 for i in self.agents}
        dones = {i: self.episode_step >= self.max_steps for i in self.agents}
        infos = {i: {"has_task": True, "effective_action": 0} for i in self.agents}
        dones["__all__"] = self.episode_step >= self.max_steps
        return obs, rewards, dones, infos

    def close(self):
        if self.use_ns3gym and self.env is not None:
            self.env.close()
