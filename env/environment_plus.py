import os
import sys
import numpy as np

class V2XEnvPlus:
    """
    Formal, unambiguous MA-ROPE+ Environment.
    
    API: Custom parallel multi-agent dictionary API.
    - reset(seed) -> obs_dict
    - step(actions_dict) -> obs_dict, rewards_dict, dones_dict, infos_dict
    
    Global Termination Rule: 
    The episode ends globally when `dones_dict["__all__"] == True`. 
    There are no individual vehicle terminations.
    """
    def __init__(self, n_vehicles=16, seed=None, f_mec=50e9, bg_workload_enabled=False):
        super(V2XEnvPlus, self).__init__()
        self.n_vehicles = n_vehicles
        self.f_mec = f_mec
        self.bg_workload_enabled = bg_workload_enabled
        self.bg_phi = 0.9
        self.bg_mu = 5e6 # 5M cycles avg background load per slot
        self.bg_max = 20e6
        self.W_t_bg = 0.0
        self.max_steps = 100
        self.episode_step = 0
        
        self.np_random = np.random.default_rng(seed)
        
        # 1. Action Space (MA-ROPE+ Phase-1)
        # Distinct from historical 4-RAT implementation.
        # 0: Local (0.0)
        # 1-5: LTE (0.2, 0.4, 0.6, 0.8, 1.0)
        # 6-10: 5G (0.2, 0.4, 0.6, 0.8, 1.0)
        self.action_map = {0: ("local", 0.0)}
        for i, rho in enumerate([0.2, 0.4, 0.6, 0.8, 1.0]):
            self.action_map[i+1] = ("LTE", rho)
            self.action_map[i+6] = ("5G", rho)
        
        # System Constants
        self.f_local = 2e9        # 2 GHz
        self.kappa_cpu = 1e-27
        self.P_tx_lte = 1.0       # Watts
        self.P_tx_5g = 2.0        # Watts
        self.R_lte = 10e6         # 10 Mbps
        self.R_5g = 100e6         # 100 Mbps
        self.eta_lte = 0.5
        self.eta_5g = 0.8
        
        # Reward Weights
        self.w_s = 0.4
        self.w_t = 0.3
        self.w_e = 0.2
        self.w_q = 0.05
        self.w_o = 0.05
        
        # Normalizers
        self.Q_max = 100e6        # 100M cycles max queue for penalty scaling
        self.B_ref = 50 * 8 * 1024 # 50 KB in bits
        
        # State tracking
        self.Q_t = 0.0
        self.W_t_prev = 0.0
        self.active_tasks = {}
        
    def _sample_task(self):
        # 65% Safety, 20% Infotainment, 15% Compute
        val = self.np_random.uniform()
        if val < 0.65:
            # Safety
            return {"class": 1, "D": 0.1, "B": 2400, "L": 1e6}
        elif val < 0.85:
            # Infotainment
            return {"class": 2, "D": 0.5, "B": 10 * 8 * 1024, "L": 5e6}
        else:
            # Compute
            return {"class": 3, "D": 1.0, "B": 50 * 8 * 1024, "L": 15e6}
            
    def _get_obs(self):
        obs = {}
        for i in range(self.n_vehicles):
            vec = np.zeros(20, dtype=np.float32)
            # Global
            vec[0] = self.episode_step / self.max_steps
            vec[1] = min(1.0, self.Q_t / self.Q_max)
            vec[2] = min(1.0, self.W_t_prev / self.Q_max)
            
            # Local physics
            pos = self.vehicles[i]["pos"]
            speed = self.vehicles[i]["speed"]
            batt = self.vehicles[i]["battery"]
            
            # Calculate distance to RSU at center of road (1300m)
            dist = abs(pos - 1300.0) + 1.0 # +1 to avoid div by zero
            # Simple path loss: gamma = P_tx / (N0 * dist^2) -> just mock inverse square scaled
            gamma_lte = np.clip(1000.0 / (dist / 100.0)**2, 10.0, 1000.0)
            gamma_5g = np.clip(1000.0 / (dist / 80.0)**2, 10.0, 1000.0)
            
            # Save for step
            self.vehicles[i]["gamma_lte"] = gamma_lte
            self.vehicles[i]["gamma_5g"] = gamma_5g
            
            p_lte = 1.0 - np.exp(-self.eta_lte * gamma_lte)
            p_5g = 1.0 - np.exp(-self.eta_5g * gamma_5g)
            
            vec[3] = p_lte
            vec[4] = p_5g
            vec[5] = pos / self.L_road
            vec[6] = (speed - 10.0) / 20.0
            vec[7] = batt / 10000.0
            vec[8] = np.clip((np.log10(gamma_lte) - 1.0) / 2.0, 0.0, 1.0)
            vec[9] = np.clip((np.log10(gamma_5g) - 1.0) / 2.0, 0.0, 1.0)
            
            # Task
            if i in self.active_tasks:
                task = self.active_tasks[i]
                vec[10] = 1.0
                vec[11] = 1.0 if task["class"] == 1 else 0.0
                vec[12] = 1.0 if task["class"] == 2 else 0.0
                vec[13] = 1.0 if task["class"] == 3 else 0.0
                vec[14] = min(1.0, (self.Q_t / self.f_mec) / 1.0) # max D is 1.0
                vec[15] = task["D"] / 1.0
                vec[16] = task["L"] / 15e6
                vec[17] = task["B"] / self.B_ref
                
            obs[i] = vec
        return obs
        
    def reset(self, seed=None):
        if seed is not None:
            self.np_random = np.random.default_rng(seed)
        self.episode_step = 0
        self.Q_t = 0.0
        self.W_t_prev = 0.0
        self.W_t_bg = 0.0
        
        # Init vehicles
        self.L_road = 2600.0
        self.vehicles = {}
        for i in range(self.n_vehicles):
            self.vehicles[i] = {
                "pos": self.np_random.uniform(0, self.L_road),
                "speed": self.np_random.uniform(10.0, 30.0),
                "battery": 10000.0,
                "gamma_lte": 100.0,
                "gamma_5g": 100.0
            }
        
        self.active_tasks = {}
        for i in range(self.n_vehicles):
            if self.np_random.uniform() < 0.3:
                self.active_tasks[i] = self._sample_task()
                
        return self._get_obs()

    def step(self, actions_dict):
        rewards = {}
        infos = {}
        
        # Populate base physics for all vehicles
        for i in range(self.n_vehicles):
            infos[i] = {
                "battery_j": self.vehicles[i]["battery"], 
                "uplink_sinr": self.vehicles[i]["gamma_lte"], # Just use LTE for eligibility proxy
                "local_sample_count": 100, # Stub
                "requested_action": actions_dict.get(i, 0),
                "effective_action": actions_dict.get(i, 0) if i in self.active_tasks else 0,
                "has_task": i in self.active_tasks
            }
        
        # 1. Evaluate Transmissions
        successful_workload = 0.0
        tx_success = {}
        
        for i, task in self.active_tasks.items():
            action = infos[i]["effective_action"]
            rat, rho = self.action_map[action]
            
            if rho > 0:
                gamma = self.vehicles[i]["gamma_lte"] if rat == "LTE" else self.vehicles[i]["gamma_5g"]
                eta = self.eta_lte if rat == "LTE" else self.eta_5g
                
                p_radio = 1.0 - np.exp(-eta * gamma)
                success = (self.np_random.uniform() < p_radio)
                tx_success[i] = success
                if success:
                    successful_workload += rho * task["L"]
            else:
                tx_success[i] = True # Local always "transmits" successfully internally
                
        # 2. Queue Update
        if self.bg_workload_enabled:
            # Autoregressive background process
            noise = self.np_random.normal(0, 1e6)
            self.W_t_bg = np.clip(self.bg_phi * self.W_t_bg + (1 - self.bg_phi) * self.bg_mu + noise, 0, self.bg_max)
        else:
            self.W_t_bg = 0.0
            
        total_workload = successful_workload + self.W_t_bg
        self.W_t_prev = total_workload
        self.dt = 0.1
        
        Q_next = max(0.0, self.Q_t + total_workload - self.f_mec * self.dt) 
        Q_current = self.Q_t # Queue seen by arriving tasks
        self.Q_t = Q_next
        
        # Mobility update for next slot
        for i in range(self.n_vehicles):
            self.vehicles[i]["pos"] = (self.vehicles[i]["pos"] + self.vehicles[i]["speed"] * self.dt) % self.L_road
        
        # 3. Latency & Energy Evaluation
        for i, task in self.active_tasks.items():
            action = infos[i]["effective_action"]
            rat, rho = self.action_map[action]
            
            L = task["L"]
            B = task["B"]
            D = task["D"]
            
            # Local
            t_local = ((1.0 - rho) * L) / self.f_local
            e_local = self.kappa_cpu * (self.f_local**2) * ((1.0 - rho) * L)
            e_ref = self.kappa_cpu * (self.f_local**2) * L
            
            # Remote
            if rho > 0:
                R_tx = self.R_lte if rat == "LTE" else self.R_5g
                P_tx = self.P_tx_lte if rat == "LTE" else self.P_tx_5g
                
                t_tx = (rho * B) / R_tx
                e_tx = P_tx * t_tx
                # Only wait in queue and execute if transmission succeeded
                if tx_success[i]:
                    t_queue = Q_current / self.f_mec
                    t_mec = (rho * L) / self.f_mec
                else:
                    t_queue = 0.0
                    t_mec = 0.0
                
                t_total = max(t_local, t_tx + t_queue + t_mec)
                e_total = e_local + e_tx
            else:
                t_total = t_local
                e_total = e_local
                
            # Deduct energy
            self.vehicles[i]["battery"] = max(0.0, self.vehicles[i]["battery"] - e_total)
            
            # 4. Success Condition
            if rho == 0.0:
                S_i = 1.0 if t_total <= D else 0.0
            else:
                S_i = 1.0 if (tx_success[i] and t_total <= D) else 0.0
                
            # 5. Utilities
            u_T = np.exp(-t_total / D)
            u_E = np.exp(-e_total / e_ref)
            u_Q = min(1.0, Q_current / self.Q_max) # Ensure penalty is scaled
            u_comm = min(1.0, (rho * B) / self.B_ref)
            
            U_i = self.w_s * S_i + self.w_t * u_T + self.w_e * u_E - self.w_q * u_Q - self.w_o * u_comm

            
            rewards[i] = U_i
            infos[i].update({
                "S_i": S_i,
                "T_i": t_total,
                "E_i": e_total,
                "u_T": u_T,
                "u_E": u_E,
                "u_Q": u_Q,
                "u_comm": u_comm,
            })
            
        self.episode_step += 1
        dones = {"__all__": self.episode_step >= self.max_steps}
        
        # Resample active tasks
        self.active_tasks = {}
        for i in range(self.n_vehicles):
            if self.np_random.uniform() < 0.3:
                self.active_tasks[i] = self._sample_task()
                
        return self._get_obs(), rewards, dones, infos
