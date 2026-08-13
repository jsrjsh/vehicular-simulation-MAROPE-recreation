import math

TASKS = {
    "safety": {"D": 100.0, "data": 0.1, "cycles": 1e8, "alpha": 0.7, "beta": 0.3, "speedup": 1.5},
    "infotainment": {"D": 500.0, "data": 2.0, "cycles": 5e8, "alpha": 0.4, "beta": 0.6, "speedup": 1.0},
    "compute": {"D": 1000.0, "data": 5.0, "cycles": 2e9, "alpha": 0.2, "beta": 0.8, "speedup": 1.0}
}

RATS = {
    "LTE": {"prop": 20.0, "tput": 50.0, "energy": 1.5},
    "ITS-G5": {"prop": 10.0, "tput": 27.0, "energy": 2.0},
    "WiFi-6": {"prop": 5.0, "tput": 600.0, "energy": 1.0},
    "5G": {"prop": 1.0, "tput": 1000.0, "energy": 0.8}
}

CPU_FREQ = 2e9
P_CPU = 2.0

def calc():
    for t_name, t in TASKS.items():
        print(f"\n--- {t_name.upper()} TASK ---")
        l_local_full = (t["cycles"] / CPU_FREQ) * 1000.0
        e_local_full = P_CPU * (l_local_full / 1000.0)
        print(f"Local Energy: {e_local_full} J")
        
        for r_name, r in RATS.items():
            print(f"  {r_name}:")
            for rho in [0.25, 0.50, 0.75, 1.0]:
                l_loc_rho = l_local_full * (1.0 - rho)
                e_loc_rho = P_CPU * (l_loc_rho / 1000.0)
                e_tx = (r["energy"] * t["data"] * rho) / 1000.0
                e_total = e_loc_rho + e_tx
                
                print(f"    Rho={rho:.2f} -> E_loc={e_loc_rho:.4f} J, E_tx={e_tx:.4f} J, E_tot={e_total:.4f} J")

calc()
