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
REMOTE_BASE = 0.5e-3 # 0.5 ms per MB

def calc():
    for t_name, t in TASKS.items():
        print(f"\n--- {t_name.upper()} TASK ---")
        l_local_full = (t["cycles"] / CPU_FREQ) * 1000.0
        print(f"Local Compute: {l_local_full} ms")
        
        for r_name, r in RATS.items():
            print(f"  {r_name}:")
            for rho in [0.25, 0.50, 0.75, 1.0]:
                l_loc_rho = l_local_full * (1.0 - rho)
                l_prop = r["prop"]
                l_tx = (t["data"] * rho * 8.0 / r["tput"]) * 1000.0
                l_remote = (t["data"] * rho * (REMOTE_BASE / t["speedup"])) * 1000.0
                l_queue = 0.0 # From instructions "Assume negligible for isolation" but actually it asks to show queue = 0 (since N=8 fasttrack had very low backlog)
                
                l_offload = l_prop + l_tx
                l_total = max(l_loc_rho, l_remote + l_queue + l_offload)
                
                print(f"    Rho={rho:.2f} -> L_loc={l_loc_rho:.2f}, L_prop={l_prop:.2f}, L_tx={l_tx:.2f}, L_rem={l_remote:.2f}, L_off={l_offload:.2f}, L_tot={l_total:.2f}")

calc()
