# agents/privacy/gaussian_ldp.py
"""
Mathematical implementation of Local Differential Privacy (LDP) using Gaussian perturbation.
Applies global L2 norm clipping and adds zero-mean Gaussian noise.
"""

import copy
import torch

def apply_gaussian_ldp(update_state_dict: dict,
                       clip_norm: float,
                       noise_multiplier: float,
                       seed: int) -> tuple:
    """
    Applies global L2 norm clipping and adds zero-mean Gaussian noise to a client model update.
    Formula:
      Delta_clipped = Delta * min(1, C / (||Delta||_2 + eta))
      Delta_private = Delta_clipped + N(0, sigma^2 C^2 I)
      
    Returns:
      (private_update, unclipped_norm, clipped_norm, noise_norm, snr, clipping_occurred)
      
    Rejects:
      - clip_norm <= 0
      - noise_multiplier < 0
      - NaN/Inf parameters in update_state_dict
    """
    if clip_norm <= 0:
        raise ValueError("Clipping norm C must be positive.")
    if noise_multiplier < 0:
        raise ValueError("Noise multiplier sigma cannot be negative.")
        
    # Check for NaN/Inf in inputs
    for k, p in update_state_dict.items():
        if not torch.isfinite(p).all():
            raise ValueError(f"Parameter '{k}' contains NaN or Inf values before LDP.")
            
    # Initialize Generator for reproducible seeded privacy noise
    generator = torch.Generator().manual_seed(seed)
    
    # 1. Compute global L2 norm across all parameters
    total_sq_sum = 0.0
    for p in update_state_dict.values():
        total_sq_sum += torch.sum(p ** 2).item()
    unclipped_norm = torch.sqrt(torch.tensor(total_sq_sum)).item()
    
    # 2. Compute clipping factor
    clipping_occurred = unclipped_norm > clip_norm
    clip_factor = min(1.0, clip_norm / (unclipped_norm + 1e-9))
    
    # 3. Apply norm clipping
    clipped_update = {}
    for k, p in update_state_dict.items():
        clipped_update[k] = p * clip_factor
    clipped_norm = unclipped_norm * clip_factor
    
    # 4. Generate and add zero-mean Gaussian noise: N(0, sigma^2 * C^2 * I)
    noise_std = noise_multiplier * clip_norm
    private_update = {}
    noise_sq_sum = 0.0
    
    for k, p in clipped_update.items():
        if noise_std > 0.0:
            noise = torch.randn(p.shape, generator=generator) * noise_std
            noise_sq_sum += torch.sum(noise ** 2).item()
            private_update[k] = p + noise
        else:
            private_update[k] = p.clone()
            
    noise_norm = torch.sqrt(torch.tensor(noise_sq_sum)).item()
    snr = clipped_norm / (noise_norm + 1e-9)
    
    return private_update, unclipped_norm, clipped_norm, noise_norm, snr, clipping_occurred
