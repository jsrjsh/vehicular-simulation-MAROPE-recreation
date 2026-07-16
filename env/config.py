# env/config.py
"""
Authoritative global configurations and constants for the MA-ROPE simulation platform.
Values are preserved exactly as defined in the recreation guide.
FORMULA_REVISION = 2026-05-08-safety-mec-lte-mask
"""

# 1.1 Compute / energy constants
CPU_FREQ_HZ = 2e9                  # Local CPU frequency (Hz)
P_CPU_W = 2.0                      # Local CPU power consumption (Watts)
SAFETY_REMOTE_MEC_SPEEDUP = 1.5    # Remote computing speedup factor for safety tasks
remote_factor_base = 0.5e-3        # Base MEC computing factor (s/MB)
DELAY_PER_UNIT_MS = 35.0           # Latency per unit of RSU queue backlog (ms)
OBS_DIM = 12                       # Dimension of vehicle observations

# 1.2 & 1.3 Channel and Physical Layer parameters per RAT index
# 0: Local, 1: LTE, 2: ITS-G5, 3: WiFi-6, 4: 5G-NR
RAT_SPECS = {
    0: {
        "name": "Local",
        "latency_ms": 0.0,
        "bandwidth_mhz": None,
        "cpu_cycles": 1e9,
        "tx_energy_mj": 0.0,
        "noise_dbm": None,
        "shadow_sigma_db": None,
        "sinr_thresh_db": None,
        "fading": "none",
        "freq_ghz": None,
        "tx_power_dbm": None,
        "path_loss_model": "none"
    },
    1: {
        "name": "LTE",
        "latency_ms": 20.0,
        "bandwidth_mhz": None,
        "cpu_cycles": 50.0,
        "tx_energy_mj": 1.5,
        "noise_dbm": -110.0,
        "shadow_sigma_db": 4.0,
        "sinr_thresh_db": 4.0,
        "fading": "jakes",
        "freq_ghz": 1.8,
        "tx_power_dbm": 23.0,
        "path_loss_model": "3gpp_v2x"
    },
    2: {
        "name": "ITS_G5",
        "latency_ms": 10.0,
        "bandwidth_mhz": None,
        "cpu_cycles": 27.0,
        "tx_energy_mj": 2.0,
        "noise_dbm": -90.0,
        "shadow_sigma_db": 4.0,
        "sinr_thresh_db": 4.0,
        "fading": "constant",
        "freq_ghz": 5.9,
        "tx_power_dbm": 23.0,
        "path_loss_model": "3gpp_v2x"
    },
    3: {
        "name": "WiFi6",
        "latency_ms": 5.0,
        "bandwidth_mhz": None,
        "cpu_cycles": 600.0,
        "tx_energy_mj": 1.0,
        "noise_dbm": -90.0,
        "shadow_sigma_db": 3.0,
        "sinr_thresh_db": 5.0,
        "fading": "constant",
        "freq_ghz": 5.0,
        "tx_power_dbm": 20.0,
        "path_loss_model": "wifi_ax"
    },
    4: {
        "name": "5GNR",
        "latency_ms": 1.0,
        "bandwidth_mhz": None,
        "cpu_cycles": 1000.0,
        "tx_energy_mj": 0.8,
        "noise_dbm": -110.0,
        "shadow_sigma_db": 4.0,
        "sinr_thresh_db": 4.0,
        "fading": "jakes",
        "freq_ghz": 3.5,
        "tx_power_dbm": 23.0,
        "path_loss_model": "5g_umi"
    }
}

# 1.4 Action Map (11 discrete actions)
# index -> (rat_idx, rho)
ACTION_MAP = {
    0: (0, 0.00),      # Local only
    1: (1, 0.25),      # LTE 25%
    2: (1, 0.50),      # LTE 50%
    3: (1, 0.75),      # LTE 75%
    4: (2, 0.25),      # ITS-G5 25%
    5: (2, 0.50),      # ITS-G5 50%
    6: (4, 0.25),      # 5G 25%
    7: (4, 0.50),      # 5G 50%
    8: (4, 1.00),      # 5G 100% (AllOffload)
    9: (3, 0.50),      # WiFi 50%
    10: (3, 1.00)      # WiFi 100%
}

# 1.5 Task Types
# name -> (D_ms, data_mb, cpu_cycles, alpha, beta)
TASK_TYPES = {
    "safety": {
        "D_ms": 100.0,
        "data_mb": 0.1,
        "cpu_cycles": 1e8,
        "alpha": 0.70,
        "beta": 0.30
    },
    "infotainment": {
        "D_ms": 500.0,
        "data_mb": 2.0,
        "cpu_cycles": 5e8,
        "alpha": 0.40,
        "beta": 0.60
    },
    "compute": {
        "D_ms": 1000.0,
        "data_mb": 5.0,
        "cpu_cycles": 2e9,
        "alpha": 0.20,
        "beta": 0.80
    }
}

# 1.7 Scenarios
# key -> task mix probabilities: P(safety), P(infotainment), P(compute)
SCENARIOS = {
    "urllc": [0.65, 0.20, 0.15],
    "balanced": [0.33, 0.33, 0.34],
    "compute": [0.10, 0.30, 0.60]
}

# 1.8 Environment Defaults
DEFAULT_N_VEHICLES = 4
DEFAULT_ROAD_LENGTH_M = 2600.0
DEFAULT_RSU_POSITIONS = [500.0, 1500.0]
DEFAULT_TASK_ARRIVAL_PROB = 0.3
DEFAULT_MAX_STEPS = 200
DEFAULT_INCLUDE_RSU_QUEUE = True
