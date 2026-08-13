import numpy as np
import pandas as pd

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def evaluate_candidates():
    # Test cases:
    # 1. Uncongested: T=0.01, D=0.1, E=5mJ, E_ref=50mJ
    # 2. Borderline Success: T=0.09, D=0.1, E=5mJ, E_ref=50mJ
    # 3. SLA Violation (Energy Saver): T=0.15, D=0.1, E=5mJ, E_ref=50mJ
    # 4. Local Execution: T=0.005, D=0.1, E=50mJ, E_ref=50mJ
    # 5. Numerical Explosion Check: T=10.0, D=0.1, E=5mJ, E_ref=50mJ
    
    test_cases = [
        {"name": "Uncongested 5G", "T": 0.01, "D": 0.1, "E": 5, "E_ref": 50, "S": 1},
        {"name": "Borderline 5G", "T": 0.09, "D": 0.1, "E": 5, "E_ref": 50, "S": 1},
        {"name": "Local Execution", "T": 0.005, "D": 0.1, "E": 50, "E_ref": 50, "S": 1},
        {"name": "SLA Violation 5G", "T": 0.15, "D": 0.1, "E": 5, "E_ref": 50, "S": 0},
        {"name": "Extreme Violation 5G", "T": 10.0, "D": 0.1, "E": 5, "E_ref": 50, "S": 0}
    ]
    
    candidates = {}
    
    # Original Reward (Baseline)
    def orig_reward(c):
        return 0.4*c["S"] + 0.3*np.exp(-c["T"]/c["D"]) + 0.2*np.exp(-c["E"]/c["E_ref"])
        
    # Candidate A: Rescaled Linear (SLA weight = 1.0, others smaller)
    def cand_a(c):
        return 1.0*c["S"] + 0.2*np.exp(-c["T"]/c["D"]) + 0.1*np.exp(-c["E"]/c["E_ref"])
        
    # Candidate B: Piecewise
    def cand_b(c):
        if c["S"] == 1:
            return 0.5*np.exp(-c["T"]/c["D"]) + 0.5*np.exp(-c["E"]/c["E_ref"])
        else:
            return -1.0
            
    # Candidate C: Smooth Sigmoid (k=50)
    def cand_c(c):
        k = 50
        u_lat = 1 - sigmoid(k * (c["T"] - c["D"]))
        return 0.5*u_lat + 0.5*np.exp(-c["E"]/c["E_ref"])
        
    # Candidate D: Lexicographic (Energy is multiplied by S)
    def cand_d(c):
        alpha = 2.0
        return np.exp(-c["T"]/c["D"]) - alpha*max(0, c["T"] - c["D"]) + 0.5*np.exp(-c["E"]/c["E_ref"])*c["S"]
        
    # Candidate E: Exponential (Clipped)
    def cand_e(c):
        pen = min(10.0, np.exp(max(0, c["T"] - c["D"])*10) - 1)
        return 0.4*c["S"] + 0.3*np.exp(-c["T"]/c["D"]) + 0.2*np.exp(-c["E"]/c["E_ref"]) - pen

    funcs = {
        "Original": orig_reward,
        "A (Rescaled)": cand_a,
        "B (Piecewise)": cand_b,
        "C (Sigmoid)": cand_c,
        "D (Lexicographic)": cand_d,
        "E (Exponential)": cand_e
    }
    
    results = {name: [] for name in funcs.keys()}
    
    for case in test_cases:
        for name, func in funcs.items():
            results[name].append(func(case))
            
    df = pd.DataFrame(results, index=[c["name"] for c in test_cases])
    print(df.round(4))
    
    # Sanity Checks
    print("\n--- SANITY CHECKS ---")
    for name in funcs.keys():
        res = df[name]
        
        # 1. Monotonicity (Latency)
        mono_lat = res["Uncongested 5G"] > res["Borderline 5G"]
        
        # 2. SLA Domination (Local vs SLA Violation 5G)
        sla_dom = res["Local Execution"] > res["SLA Violation 5G"]
        
        # 3. Numerical Explosion
        num_safe = res["Extreme Violation 5G"] > -15.0 and not np.isnan(res["Extreme Violation 5G"])
        
        passes = mono_lat and sla_dom and num_safe
        
        print(f"{name:15}: SLA_DOM={sla_dom}, MONO_LAT={mono_lat}, SAFE={num_safe} => PASS={passes}")

if __name__ == "__main__":
    evaluate_candidates()
