# env/environment.py
"""
Deterministic multi-agent environment core for V2X task offloading in MA-ROPE.
Implements vehicle mobility, RSU queue workloads, task generation, latency/energy costs,
observation building, and reward evaluation.
"""

import math
import numpy as np
from typing import Dict, Any, Tuple
from env.config import (
    CPU_FREQ_HZ, P_CPU_W, SAFETY_REMOTE_MEC_SPEEDUP, remote_factor_base,
    DELAY_PER_UNIT_MS, OBS_DIM, RAT_SPECS, ACTION_MAP, TASK_TYPES, SCENARIOS,
    DEFAULT_N_VEHICLES, DEFAULT_ROAD_LENGTH_M, DEFAULT_RSU_POSITIONS,
    DEFAULT_TASK_ARRIVAL_PROB, DEFAULT_MAX_STEPS, DEFAULT_INCLUDE_RSU_QUEUE
)
from env.channel import compute_sinr, compute_link_success

class V2XEnv:
    """
    Multi-Agent V2X Offloading Environment.
    Implements a dictionary-based multi-agent API.
    """
    def __init__(self,
                 n_vehicles: int = DEFAULT_N_VEHICLES,
                 road_length_m: float = DEFAULT_ROAD_LENGTH_M,
                 rsu_positions: list = DEFAULT_RSU_POSITIONS,
                 scenario: str = "urllc",
                 task_arrival_prob: float = DEFAULT_TASK_ARRIVAL_PROB,
                 max_steps: int = DEFAULT_MAX_STEPS,
                 include_rsu_queue: bool = DEFAULT_INCLUDE_RSU_QUEUE,
                 seed: int = None):
        
        self.n_vehicles = n_vehicles
        self.road_length_m = road_length_m
        self.rsu_positions = rsu_positions
        self.scenario_name = scenario.lower()
        self.task_arrival_prob = task_arrival_prob
        self.max_steps = max_steps
        self.include_rsu_queue = include_rsu_queue
        
        if self.scenario_name not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {self.scenario_name}")
            
        self.task_mix = SCENARIOS[self.scenario_name]
        self.seed_val = seed
        self.rng = np.random.RandomState(seed)
        
        # Vehicle agent identifiers (0 to N-1)
        self.agents = list(range(self.n_vehicles))
        
        # State variables
        self.positions = np.zeros(self.n_vehicles)
        self.speeds = np.zeros(self.n_vehicles)
        self.batteries = np.zeros(self.n_vehicles)
        self.active_tasks = {}  # agent_id -> task_dict
        
        # Episode metrics and counters per agent
        # agent_id -> rat_idx -> counter
        self.tx_counters = {}
        self.rx_counters = {}
        self.rx_on_time_counters = {}
        self.total_offload_transmissions = 0  # Global count of any offloading across all RATs
        
        # RSU state
        self.rsu_queues = {r_idx: 0.0 for r_idx in range(len(self.rsu_positions))}
        self.rsu_cbr_prev = {r_idx: 0.0 for r_idx in range(len(self.rsu_positions))}
        self.rsu_cbr_curr = {r_idx: 0.0 for r_idx in range(len(self.rsu_positions))}
        
        self.episode_step = 0

    def _toroidal_distance(self, x1: float, x2: float) -> float:
        """Computes toroidal distance along the circular road ring."""
        diff = abs(x1 - x2)
        return min(diff, self.road_length_m - diff)

    def _get_nearest_rsu(self, pos: float) -> int:
        """Returns the index of the nearest RSU."""
        distances = [self._toroidal_distance(pos, rsu_pos) for rsu_pos in self.rsu_positions]
        return int(np.argmin(distances))

    def _sample_task(self) -> Dict[str, Any]:
        """Samples a new task from the scenario mix."""
        task_keys = list(TASK_TYPES.keys())
        chosen_key = self.rng.choice(task_keys, p=self.task_mix)
        task_data = TASK_TYPES[chosen_key].copy()
        task_data["type"] = chosen_key
        return task_data

    def get_empirical_prr(self, agent_id: int, rat_idx: int) -> float:
        """
        Computes the empirical PRR for the given RAT.
        If no samples exist, falls back to the observation defaults:
        0.5 if there are global offload transmissions, else 1.0.
        """
        tx = self.tx_counters[agent_id][rat_idx]
        if tx > 0:
            return self.rx_counters[agent_id][rat_idx] / tx
        else:
            return 0.5 if self.total_offload_transmissions > 0 else 1.0

    def reset(self, seed: int = None) -> Dict[int, np.ndarray]:
        """Resets the environment state."""
        if seed is not None:
            self.seed_val = seed
            self.rng = np.random.RandomState(seed)
            
        self.episode_step = 0
        self.total_offload_transmissions = 0
        
        # Initialize vehicle attributes
        for i in self.agents:
            self.positions[i] = self.rng.uniform(8.0, self.road_length_m)
            self.speeds[i] = self.rng.uniform(20.0, 38.0)
            self.batteries[i] = self.rng.uniform(70.0, 100.0)
            self.active_tasks[i] = self._sample_task()
            
            # Reset episode packet counters
            self.tx_counters[i] = {r: 0 for r in range(1, 5)}
            self.rx_counters[i] = {r: 0 for r in range(1, 5)}
            self.rx_on_time_counters[i] = {r: 0 for r in range(1, 5)}
            
        # Reset RSU queues
        for r_idx in range(len(self.rsu_positions)):
            self.rsu_queues[r_idx] = 0.0
            self.rsu_cbr_prev[r_idx] = 0.0
            self.rsu_cbr_curr[r_idx] = 0.0
            
        return self._build_observations()

    def _build_observations(self) -> Dict[int, np.ndarray]:
        """Constructs 12-dimensional normalized observations for all agents."""
        obs_dict = {}
        for i in self.agents:
            obs = np.zeros(OBS_DIM, dtype=np.float32)
            pos = self.positions[i]
            rsu_idx = self._get_nearest_rsu(pos)
            rsu_pos = self.rsu_positions[rsu_idx]
            dist = self._toroidal_distance(pos, rsu_pos)
            speed = self.speeds[i]
            
            # 1. Normalized SINRs per RAT (features 0-3)
            for r_idx in range(1, 5):
                # Sample instantaneous SINR (fading and shadow are modeled)
                sinr_db = compute_sinr(r_idx, dist, speed, self.rng)
                obs[r_idx - 1] = np.clip((sinr_db + 20.0) / 60.0, 0.0, 1.0)
                
            # 2. Empirical PRR per RAT (features 4-7)
            for r_idx in range(1, 5):
                obs[r_idx + 3] = self.get_empirical_prr(i, r_idx)
                
            # 3. Normalized RSU queue size (feature 8)
            q_size = self.rsu_queues[rsu_idx]
            obs[8] = np.clip(q_size / self.n_vehicles, 0.0, 1.0)
            
            # 4. Normalized data size (feature 9)
            task = self.active_tasks[i]
            obs[9] = task["data_mb"] / 5.0
            
            # 5. Normalized deadline (feature 10)
            obs[10] = task["D_ms"] / 2000.0
            
            # 6. Normalized battery (feature 11)
            obs[11] = self.batteries[i] / 100.0
            
            obs_dict[i] = obs
        return obs_dict

    def step(self, actions: Dict[int, int]) -> Tuple[Dict[int, np.ndarray], Dict[int, float], Dict[int, bool], Dict[str, Any]]:
        """Advances the environment dynamics by one step."""
        if len(actions) != self.n_vehicles:
            raise ValueError(f"Action count ({len(actions)}) must match vehicle count ({self.n_vehicles})")
            
        self.episode_step += 1
        
        # 1. Decode actions and update RSU queue workloads
        decoded_actions = {}
        rsu_workloads = {r_idx: [] for r_idx in range(len(self.rsu_positions))}
        
        for i in self.agents:
            act_idx = actions[i]
            if act_idx not in ACTION_MAP:
                raise ValueError(f"Invalid action index {act_idx} for vehicle {i}")
            rat_idx, rho = ACTION_MAP[act_idx]
            decoded_actions[i] = (rat_idx, rho)
            
            rsu_idx = self._get_nearest_rsu(self.positions[i])
            if rat_idx > 0 and rho > 0.0:
                rsu_workloads[rsu_idx].append((i, rat_idx, rho))
                
        # Aggregate Q_r for each RSU
        # Sum of the requested offloading ratios of connected offloading vehicles
        for r_idx in range(len(self.rsu_positions)):
            self.rsu_queues[r_idx] = sum(item[2] for item in rsu_workloads[r_idx])
            self.rsu_cbr_prev[r_idx] = self.rsu_cbr_curr[r_idx]
            self.rsu_cbr_curr[r_idx] = np.clip(self.rsu_queues[r_idx] / self.n_vehicles, 0.0, 1.0)
            
        # 2. Compute SINRs and adapt offloading ratio (SINR-proportional ρ)
        adapted_rhos = {}
        sinrs = {}
        for i in self.agents:
            rat_idx, rho = decoded_actions[i]
            pos = self.positions[i]
            rsu_idx = self._get_nearest_rsu(pos)
            rsu_pos = self.rsu_positions[rsu_idx]
            dist = self._toroidal_distance(pos, rsu_pos)
            speed = self.speeds[i]
            
            # Instantly evaluate link SINRs for selected RAT and other RATs
            veh_sinrs = {}
            for r_idx in range(1, 5):
                veh_sinrs[r_idx] = compute_sinr(r_idx, dist, speed, self.rng)
            sinrs[i] = veh_sinrs
            
            if rat_idx == 0 or rho == 0.0:
                adapted_rhos[i] = 0.0
            else:
                # Calculate SINR proportion
                gammas = {r: max(10**(veh_sinrs[r] / 10.0), 1e-6) for r in range(1, 5)}
                sum_gammas = sum(gammas.values())
                q_r = gammas[rat_idx] / sum_gammas
                
                # Rescale and clip chosen offloading ratio
                adapted_rhos[i] = np.clip(rho * q_r, 0.0, 1.0)

        # 3. Compute Latency and Energy costs
        latencies = {}
        energies = {}
        for i in self.agents:
            rat_idx, rho = decoded_actions[i]
            rho_prime = adapted_rhos[i]
            task = self.active_tasks[i]
            
            # Local computing latency (ms)
            l_local = (task["cpu_cycles"] / CPU_FREQ_HZ) * 1000.0
            
            if rat_idx == 0 or rho_prime == 0.0:
                l_total = l_local
                # Local computing energy (J)
                e_total = P_CPU_W * (l_total / 1000.0)
            else:
                # Remote computation latency (ms)
                remote_speed = SAFETY_REMOTE_MEC_SPEEDUP if task["type"] == "safety" else 1.0
                remote_factor = remote_factor_base / remote_speed
                l_remote = (task["data_mb"] * rho_prime * remote_factor) * 1000.0
                
                # Queuing delay (ms)
                rsu_idx = self._get_nearest_rsu(self.positions[i])
                l_queue = (self.rsu_queues[rsu_idx] * DELAY_PER_UNIT_MS) if self.include_rsu_queue else 0.0
                
                # Sidelink/transmission propagation delay (ms)
                l_offload = RAT_SPECS[rat_idx]["latency_ms"]
                
                # Parallel computation max model (core novelty)
                l_total = max(l_local * (1.0 - rho_prime), l_remote + l_queue + l_offload)
                
                # Energy consumed (J)
                tx_energy_mj = RAT_SPECS[rat_idx]["tx_energy_mj"]
                e_tx = (tx_energy_mj * task["data_mb"] * rho_prime) / 1000.0
                e_total = P_CPU_W * (l_total / 1000.0) + e_tx
                
            latencies[i] = l_total
            energies[i] = max(e_total, 0.0)

        # 4. Physical transmission Bernoulli success and counter updates
        successes = {}
        for i in self.agents:
            rat_idx, rho = decoded_actions[i]
            rho_prime = adapted_rhos[i]
            task = self.active_tasks[i]
            
            if rat_idx == 0 or rho_prime == 0.0:
                successes[i] = True  # Local processing is always reliable
            else:
                # Calculate link success probability from SINR
                sinr_db = sinrs[i][rat_idx]
                success = compute_link_success(rat_idx, sinr_db, self.rng)
                successes[i] = success
                
                # Update counters
                self.tx_counters[i][rat_idx] += 1
                self.total_offload_transmissions += 1
                if success:
                    self.rx_counters[i][rat_idx] += 1
                    if latencies[i] <= task["D_ms"]:
                        self.rx_on_time_counters[i][rat_idx] += 1

        # 5. Compute rewards (U_PRR training utility)
        rewards = {}
        for i in self.agents:
            rat_idx, rho = decoded_actions[i]
            rho_prime = adapted_rhos[i]
            task = self.active_tasks[i]
            
            if rat_idx == 0 or rho_prime == 0.0:
                prr_val = 1.0
            else:
                prr_val = self.get_empirical_prr(i, rat_idx)
                
            rsu_idx = self._get_nearest_rsu(self.positions[i])
            cbr_t_prev = self.rsu_cbr_prev[rsu_idx]
            cbr_t_curr = self.rsu_cbr_curr[rsu_idx]
            delta_cbr = np.clip(cbr_t_prev - cbr_t_curr, -0.5, 0.5)
            
            alpha = task["alpha"]
            beta = task["beta"]
            l_ratio = latencies[i] / task["D_ms"]
            e_ratio = energies[i] / 3.0
            
            # Eq. 4a training reward
            u = (alpha * prr_val
                 + (beta / 2.0) * math.exp(-l_ratio)
                 + (beta / 2.0) * math.exp(-e_ratio)
                 + (beta / 4.0) * delta_cbr)
                 
            rewards[i] = float(np.clip(u, 0.0, 1.0))

        # 6. Update vehicle mobility: toroidal wrap-around (dt = 0.1 s)
        for i in self.agents:
            self.positions[i] = (self.positions[i] + self.speeds[i] * 0.1) % self.road_length_m

        # 7. Task resampling (probability 0.3)
        for i in self.agents:
            if self.rng.uniform(0.0, 1.0) < 0.3:
                self.active_tasks[i] = self._sample_task()

        # 8. Build next observations
        next_obs = self._build_observations()
        
        # Done dictionaries
        is_done = self.episode_step >= self.max_steps
        dones = {i: is_done for i in self.agents}
        dones["__all__"] = is_done
        
        # Pack info with metrics
        infos = {}
        for i in self.agents:
            rat_idx, rho = decoded_actions[i]
            task = self.active_tasks[i]
            
            # Compute evaluation metric U_OTR
            if rat_idx == 0 or rho == 0.0:
                otr_val = 1.0
            else:
                tx = self.tx_counters[i][rat_idx]
                otr_val = self.rx_on_time_counters[i][rat_idx] / tx if tx > 0 else (0.5 if self.total_offload_transmissions > 0 else 1.0)
                
            u_otr = (task["alpha"] * otr_val
                     + (task["beta"] / 2.0) * math.exp(-latencies[i] / task["D_ms"])
                     + (task["beta"] / 2.0) * math.exp(-energies[i] / 3.0)
                     + (task["beta"] / 4.0) * (self.rsu_cbr_prev[self._get_nearest_rsu(self.positions[i])] - self.rsu_cbr_curr[self._get_nearest_rsu(self.positions[i])]))
            u_otr = float(np.clip(u_otr, 0.0, 1.0))
            
            infos[i] = {
                "latency_ms": latencies[i],
                "energy_j": energies[i],
                "transmission_success": successes[i],
                "task_type": task["type"],
                "chosen_rat": rat_idx,
                "chosen_rho": rho,
                "adapted_rho": adapted_rhos[i],
                "u_otr": u_otr,
                "empirical_prr": self.get_empirical_prr(i, rat_idx) if rat_idx > 0 else 1.0
            }
            
        return next_obs, rewards, dones, infos
