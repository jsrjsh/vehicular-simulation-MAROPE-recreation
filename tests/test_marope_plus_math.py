import math

class Approx:
    def __init__(self, expected, rel=1e-6, abs=1e-12):
        self.expected = expected
        self.rel = rel
        self.abs = abs

    def __eq__(self, actual):
        return math.isclose(actual, self.expected, rel_tol=self.rel, abs_tol=self.abs)

class PytestMock:
    approx = Approx

pytest = PytestMock()

def calc_local_latency(rho, L, f_local):
    return ((1.0 - rho) * L) / f_local

def calc_tx_latency(rho, B, R_tx):
    return (rho * B) / R_tx

def calc_mec_latency(rho, L, f_mec):
    return (rho * L) / f_mec

def calc_queue_latency(Q_t, f_mec):
    return Q_t / f_mec

def calc_total_latency(rho, L, B, f_local, f_mec, R_tx, Q_t):
    t_local = calc_local_latency(rho, L, f_local)
    if rho == 0.0:
        return t_local
    t_tx = calc_tx_latency(rho, B, R_tx)
    t_queue = calc_queue_latency(Q_t, f_mec)
    t_mec = calc_mec_latency(rho, L, f_mec)
    return max(t_local, t_tx + t_queue + t_mec)

def calc_local_energy(rho, L, f_local, kappa_cpu):
    return kappa_cpu * (f_local**2) * ((1.0 - rho) * L)

def calc_tx_energy(rho, B, R_tx, P_tx):
    t_tx = calc_tx_latency(rho, B, R_tx)
    return P_tx * t_tx

def calc_total_energy(rho, L, B, f_local, R_tx, P_tx, kappa_cpu):
    return calc_local_energy(rho, L, f_local, kappa_cpu) + calc_tx_energy(rho, B, R_tx, P_tx)

def test_local_execution():
    rho = 0.0
    L = 1e6
    B = 2400
    f_local = 2e9
    f_mec = 20e9
    R_tx = 10e6
    P_tx = 1.0
    kappa_cpu = 1e-27
    Q_t = 0
    
    t = calc_total_latency(rho, L, B, f_local, f_mec, R_tx, Q_t)
    e = calc_total_energy(rho, L, B, f_local, R_tx, P_tx, kappa_cpu)
    
    assert t == pytest.approx(0.0005)
    assert e == pytest.approx(0.004)

def test_full_offload():
    rho = 1.0
    L = 1e6
    B = 2400
    f_local = 2e9
    f_mec = 20e9
    R_tx = 10e6
    P_tx = 1.0
    kappa_cpu = 1e-27
    Q_t = 0
    
    t = calc_total_latency(rho, L, B, f_local, f_mec, R_tx, Q_t)
    e = calc_total_energy(rho, L, B, f_local, R_tx, P_tx, kappa_cpu)
    
    assert t == pytest.approx(0.00029)
    assert e == pytest.approx(0.00024)

def test_partial_offload():
    rho = 0.5
    L = 1e6
    B = 2400
    f_local = 2e9
    f_mec = 20e9
    R_tx = 10e6
    P_tx = 1.0
    kappa_cpu = 1e-27
    Q_t = 1e7
    
    t = calc_total_latency(rho, L, B, f_local, f_mec, R_tx, Q_t)
    e = calc_total_energy(rho, L, B, f_local, R_tx, P_tx, kappa_cpu)
    
    assert t == pytest.approx(0.000645)
    assert e == pytest.approx(0.00212)

if __name__ == "__main__":
    test_local_execution()
    test_full_offload()
    test_partial_offload()
    print("All analytical golden tests passed successfully!")
