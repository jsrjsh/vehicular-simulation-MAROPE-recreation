import copy
import torch

class FederatedCoordinatorPlus:
    """
    Federated Learning coordinator for MA-ROPE+ Phase B (Non-Private).
    Calculates physical eligibility dynamically per round, aggregates updates using
    strict sample-count weighting, and returns an auditable JSON report.
    """
    def __init__(self, n_agents: int, b_min: float = 100.0, gamma_min: float = 1.0, 
                 n_min: int = 10, theta_round: float = 0.9):
        self.n_agents = n_agents
        
        # Physical eligibility thresholds
        self.b_min = b_min          # Joules
        self.gamma_min = gamma_min  # Linear SINR
        self.n_min = n_min          # Local samples
        self.theta_round = theta_round
        
        self.sync_rounds = 0
        
    def _check_eligibility(self, infos_dict: dict) -> tuple:
        """
        Calculates physical eligibility for each agent.
        Returns:
            eligible_clients (list): List of client indices that passed all checks.
            ineligible_reasons (dict): Mapping of client_idx -> list of failure reasons.
        """
        eligible_clients = []
        ineligible_reasons = {}
        
        for i in range(self.n_agents):
            if i not in infos_dict:
                ineligible_reasons[i] = ["missing_info"]
                continue
                
            info = infos_dict[i]
            reasons = []
            
            b = info.get("battery_j", 0.0)
            g = info.get("uplink_sinr", 0.0)
            n = info.get("local_sample_count", 0)
            
            if b < self.b_min:
                reasons.append("battery")
            if g < self.gamma_min:
                reasons.append("sinr")
            if n < self.n_min:
                reasons.append("samples")
                
            if len(reasons) == 0:
                eligible_clients.append(i)
            else:
                ineligible_reasons[i] = reasons
                
        return eligible_clients, ineligible_reasons

    def _aggregate(self, state_dicts: list, sample_counts: list) -> dict:
        if not state_dicts:
            raise ValueError("Cannot aggregate empty list of state dicts.")
        if len(state_dicts) != len(sample_counts):
            raise ValueError("Length mismatch between state dicts and sample counts.")
            
        total_samples = sum(sample_counts)
        if total_samples <= 0:
            raise ValueError("Sum of sample counts must be positive.")
            
        weights = [float(n) / total_samples for n in sample_counts]
        ref_keys = set(state_dicts[0].keys())
        global_state = copy.deepcopy(state_dicts[0])
        
        # Zero out parameters
        for k in global_state.keys():
            if global_state[k].is_floating_point():
                global_state[k] = torch.zeros_like(global_state[k])
            else:
                # Integer buffers (e.g. num_batches_tracked). 
                # Strategy: just take the value from the first eligible client (or sum? or max?).
                # Standard PyTorch behavior for these is usually to take the server's tracked value, 
                # but federated averaging typically takes client 0's value to avoid casting issues.
                pass 
                
        for idx, sd in enumerate(state_dicts):
            if set(sd.keys()) != ref_keys:
                raise KeyError(f"Client {idx} parameter keys do not match reference keys.")
                
            for k in ref_keys:
                param = sd[k]
                if param.shape != global_state[k].shape:
                    raise ValueError(f"Client {idx} parameter '{k}' shape mismatch. Expected {global_state[k].shape}, got {param.shape}.")
                    
                if not torch.isfinite(param.float()).all():
                    raise ValueError(f"Client {idx} parameter '{k}' contains NaN or Inf values.")
                    
                if global_state[k].is_floating_point():
                    global_state[k] += weights[idx] * param.clone()
                else:
                    # Integer buffers are updated on the first pass only and left alone
                    if idx == 0:
                        global_state[k] = param.clone()
                    
        return global_state

    def aggregate_and_broadcast(self, agent_models_dict: dict, infos_dict: dict) -> tuple:
        """
        Runs one synchronous non-private aggregation round.
        Returns:
            global_state_dict: The aggregated state dict, or None if aborted.
            report: Auditable JSON dictionary.
        """
        self.sync_rounds += 1
        
        # 1. Eligibility
        eligible_clients, ineligible_reasons = self._check_eligibility(infos_dict)
        eligible_fraction = len(eligible_clients) / float(self.n_agents)
        
        report = {
            "eligible_clients": eligible_clients,
            "ineligible_reasons": ineligible_reasons,
            "eligible_fraction": eligible_fraction,
            "round_executed": False,
            "communication_bytes": {"uplink": 0, "downlink": 0}
        }
        
        # 2. Threshold Check
        if eligible_fraction < self.theta_round:
            return None, report
            
        if len(eligible_clients) == 0:
            return None, report
            
        # 3. Payload Accounting (uplink)
        # Assuming all models have the same shape
        sample_model = agent_models_dict[eligible_clients[0]]
        param_count = sum(p.numel() for p in sample_model.values())
        b_param = 4 # FP32 bytes
        model_size_bytes = param_count * b_param
        
        report["communication_bytes"]["uplink"] = len(eligible_clients) * model_size_bytes
        
        # 4. Aggregation
        state_dicts_to_aggregate = [agent_models_dict[i] for i in eligible_clients]
        sample_counts = [infos_dict[i].get("local_sample_count", 1) for i in eligible_clients]
        
        global_state = self._aggregate(state_dicts_to_aggregate, sample_counts)
        report["round_executed"] = True
        
        # Calculate Divergence (L2 norm distance from global state for eligible clients)
        divergences = []
        for sd in state_dicts_to_aggregate:
            div = 0.0
            for k in global_state.keys():
                if global_state[k].is_floating_point():
                    div += torch.sum((sd[k] - global_state[k])**2).item()
            divergences.append(div ** 0.5)
            
        report["divergence_before"] = sum(divergences) / len(divergences) if divergences else 0.0
        report["divergence_after"] = 0.0 # Since it's a hard sync for all clients
        
        # 5. Payload Accounting (downlink)
        # All N agents receive the global model
        report["communication_bytes"]["downlink"] = self.n_agents * model_size_bytes
        
        return global_state, report
