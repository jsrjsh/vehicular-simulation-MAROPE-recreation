# env/channel.py
"""
Physical layer and wireless channel modeling for the MA-ROPE simulation platform.
Implements path-loss, shadow fading, Jakes fading, SINR, and link success probability.
Supports two modes: 'physically_corrected' and 'baseline_recreation'.
"""

import math
import numpy as np
from env.config import RAT_SPECS

SPEED_OF_LIGHT = 3e8  # m/s

def compute_path_loss(rat_idx: int, distance_m: float) -> float:
    """
    Computes path loss (dB) based on the RAT model and distance.
    Equation references:
      - 3GPP V2X (LTE, ITS-G5): PL = 47.9 + 10 * log10(d/10)
      - 5G UMi (5G-NR): PL = 32.4 + 20 * log10(f_GHz) + 20 * log10(d)
      - WiFi-ax (WiFi-6): PL = 40.05 + 20 * log10(f_GHz/2.4) + 20 * log10(d)
    where d = max(distance_m, 1.0)
    """
    d = max(distance_m, 1.0)
    spec = RAT_SPECS[rat_idx]
    model = spec["path_loss_model"]
    freq_ghz = spec["freq_ghz"]

    if model == "3gpp_v2x":
        return 47.9 + 10.0 * math.log10(d / 10.0)
    elif model == "5g_umi":
        return 32.4 + 20.0 * math.log10(freq_ghz) + 20.0 * math.log10(d)
    elif model == "wifi_ax":
        return 40.05 + 20.0 * math.log10(freq_ghz / 2.4) + 20.0 * math.log10(d)
    elif model == "none":
        return 0.0
    else:
        raise ValueError(f"Unknown path loss model: {model}")

def compute_jakes_fading(rat_idx: int, speed_mps: float, rng: np.random.RandomState, mode: str = "physically_corrected") -> float:
    """
    Computes Jakes Rayleigh fading loss (dB) for the given RAT and vehicle speed.
    Active only for LTE (1) and 5GNR (4).
    If mode is 'baseline_recreation', uses the literal unscaled Doppler shift.
    If mode is 'physically_corrected', uses the converted frequency in Hz.
    """
    spec = RAT_SPECS[rat_idx]
    if spec["fading"] != "jakes":
        return 0.0

    if speed_mps < 0.1:
        return 0.0

    freq_ghz = spec["freq_ghz"]
    
    if mode == "baseline_recreation":
        # Literal unscaled formula from the recreation guide
        f_D = (speed_mps * freq_ghz) / SPEED_OF_LIGHT
    else:
        # Corrected formula scaling GHz to Hz
        f_D = (speed_mps * (freq_ghz * 1e9)) / SPEED_OF_LIGHT
        
    T_c = 0.423 / max(f_D, 1e-6)
    
    delta_t = 0.1
    r = min(delta_t / T_c, 10.0)

    # Rayleigh fading envelope A (using two independent standard normal variables)
    x1 = rng.normal(0.0, 1.0)
    x2 = rng.normal(0.0, 1.0)
    A = max(math.sqrt(x1**2 + x2**2), 1e-9)

    L_fade = (-20.0 * math.log10(A)) * min(r / 5.0, 1.5)
    return max(L_fade, 0.0)

def compute_sinr(rat_idx: int, distance_m: float, speed_mps: float, rng: np.random.RandomState, mode: str = "physically_corrected") -> float:
    """
    Computes the instantaneous SINR (dB) for a wireless link.
    If mode is 'baseline_recreation', shadowing term is squared literally as written in the guide.
    If mode is 'physically_corrected', shadowing is a standard zero-mean normal sample.
    """
    spec = RAT_SPECS[rat_idx]
    if spec["name"] == "Local":
        return float("inf")

    p_tx = spec["tx_power_dbm"]
    n_0 = spec["noise_dbm"]
    sigma_h = spec["shadow_sigma_db"]

    pl = compute_path_loss(rat_idx, distance_m)
    l_fade = compute_jakes_fading(rat_idx, speed_mps, rng, mode=mode)

    # Shadow fading
    raw_shadow = rng.normal(0.0, sigma_h)
    if mode == "baseline_recreation":
        # Literal formula: + N(0, sigma_h)^2
        x_shadow = raw_shadow ** 2
    else:
        x_shadow = raw_shadow

    sinr = p_tx - pl - n_0 + x_shadow - l_fade
    return sinr

def compute_link_success(rat_idx: int, sinr_db: float, rng: np.random.RandomState, mode: str = "physically_corrected") -> bool:
    """
    Computes the link success probability and samples a Bernoulli draw.
    """
    spec = RAT_SPECS[rat_idx]
    if spec["name"] == "Local":
        return True

    tau = spec["sinr_thresh_db"]
    sigma_h = spec["shadow_sigma_db"]

    # Sigmoid link success probability
    exponent = -(sinr_db - tau) / (3.0 * sigma_h)
    
    # Clip exponent to avoid overflow in exp()
    exponent = max(min(exponent, 100.0), -100.0)
    p = 1.0 / (1.0 + math.exp(exponent))

    # Bernoulli trial
    return bool(rng.uniform(0.0, 1.0) < p)
