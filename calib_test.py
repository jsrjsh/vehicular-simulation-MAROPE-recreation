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

REMOTE_BASE = 0.5e-3

def test_calib(freq, rem_base):
    for t_name, t in TASKS.items():
        print(f"--- {t_name.upper()} ---")
        l_loc_full = (t["cycles"] / freq) * 1000.0
        print(f"Local Full: {l_loc_full:.1f} ms (D={t['D']})")
        for r_name, r in RATS.items():
            for rho in [0.5, 1.0]:
                l_prop = r["prop"]
                l_tx = (t["data"] * rho * 8.0 / r["tput"]) * 1000.0
                l_rem = (t["data"] * rho * (rem_base / t["speedup"])) * 1000.0
                l_off = l_prop + l_tx + l_rem
                l_loc_rho = l_loc_full * (1.0 - rho)
                l_tot = max(l_loc_rho, l_off)
                print(f"  {r_name} Rho={rho}: L_loc_rho={l_loc_rho:.1f}, L_off={l_off:.1f} -> L_tot={l_tot:.1f}")

test_calib(1.0e9, 0.5e-3)
