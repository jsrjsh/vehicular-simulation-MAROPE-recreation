# agents/federated/fedavg.py
"""
Mathematical implementation of Federated Averaging (FedAvg).
Aggregates state dictionaries weighted by sample counts, with strict validation checks.
"""

import copy
import torch

def federated_averaging(state_dicts: list, sample_counts: list) -> dict:
    """
    Computes sample-count-weighted Federated Averaging on online networks.
    Formula: w_global = sum_i (n_i / sum_j n_j) * w_i
    
    Rejects:
    - Empty state dict lists.
    - Parameter key mismatches.
    - Parameter shape mismatches.
    - NaNs or infinite values.
    """
    if not state_dicts:
        raise ValueError("Cannot aggregate empty list of state dicts.")
    if len(state_dicts) != len(sample_counts):
        raise ValueError("Length mismatch between state dicts and sample counts.")
        
    total_samples = sum(sample_counts)
    if total_samples <= 0:
        raise ValueError("Sum of sample counts must be positive.")
        
    # Standardize weights
    weights = [float(n) / total_samples for n in sample_counts]
    
    # Target reference dictionary structure
    ref_keys = set(state_dicts[0].keys())
    
    # Initialize global state dict
    global_state = copy.deepcopy(state_dicts[0])
    
    # Zero out parameters
    for k in global_state.keys():
        global_state[k] = torch.zeros_like(global_state[k])
        
    # Accumulate weighted sums
    for idx, sd in enumerate(state_dicts):
        if set(sd.keys()) != ref_keys:
            raise KeyError(f"Client {idx} parameter keys do not match reference keys.")
            
        for k in ref_keys:
            param = sd[k]
            if param.shape != global_state[k].shape:
                raise ValueError(f"Client {idx} parameter '{k}' shape mismatch. Expected {global_state[k].shape}, got {param.shape}.")
                
            if not torch.isfinite(param).all():
                raise ValueError(f"Client {idx} parameter '{k}' contains NaN or Inf values.")
                
            global_state[k] += weights[idx] * param.clone()
            
    return global_state
