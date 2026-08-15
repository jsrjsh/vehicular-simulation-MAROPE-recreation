"""
scripts/compute_channel_model_golden_values.py

Produces reference ("golden") values from the REAL env/channel.py functions
for a fixed set of test cases, using a fake RNG that returns pre-programmed
values instead of drawing real random numbers. This isolates the channel
_model_ (the actual translation risk) from RNG cross-language equivalence
(numpy vs. C++ don't produce the same bits for "the same seed" anyway, so
that's not worth solving).

Companion to src/maro_pe/simulation/channel_model_golden_test.cc, which uses
the identical test cases and pre-programmed values on the C++ side. The two
outputs should match to ~1e-9 for every test case; any larger discrepancy
means the C++ translation has a bug, not that the RNGs disagree.

Usage: PYTHONPATH=<workspace root containing env/> python3 \
    scripts/compute_channel_model_golden_values.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_claude_workspace"))

from env.channel import compute_path_loss, compute_jakes_fading, compute_sinr, compute_link_success


class FakeRng:
    """Returns pre-programmed values in call order instead of real randomness.
    .normal(loc, scale) and .uniform(lo, hi) ignore their arguments except to
    apply loc/scale the same way numpy would (loc + scale * next_standard_normal)."""

    def __init__(self, standard_normals=None, uniforms=None):
        self._normals = list(standard_normals or [])
        self._uniforms = list(uniforms or [])

    def normal(self, loc=0.0, scale=1.0):
        z = self._normals.pop(0)
        return loc + scale * z

    def uniform(self, lo=0.0, hi=1.0):
        u = self._uniforms.pop(0)
        return lo + (hi - lo) * u


# (name, rat_idx, distance_m, speed_mps, jakes_z1, jakes_z2, shadow_z, link_u, mode)
TEST_CASES = [
    ("lte_300m_20mps_baseline", 1, 300.0, 20.0, 0.8, -0.3, 0.5, 0.4, "baseline_recreation"),
    ("wifi6_50m_0mps_baseline", 3, 50.0, 0.0, 0.0, 0.0, -0.7, 0.9, "baseline_recreation"),
    ("5gnr_800m_30mps_baseline", 4, 800.0, 30.0, -1.2, 0.6, 1.1, 0.1, "baseline_recreation"),
    ("itsg5_150m_15mps_baseline", 2, 150.0, 15.0, 0.3, 0.3, -0.2, 0.6, "baseline_recreation"),
    ("lte_300m_20mps_corrected", 1, 300.0, 20.0, 0.8, -0.3, 0.5, 0.4, "physically_corrected"),
]


def main():
    from env.config import RAT_SPECS

    for name, rat, dist, speed, jz1, jz2, sz, u, mode in TEST_CASES:
        pl = compute_path_loss(rat, dist)

        jakes_rng = FakeRng(standard_normals=[jz1, jz2])
        jakes_db = compute_jakes_fading(rat, speed, jakes_rng, mode=mode)

        # compute_sinr() calls compute_jakes_fading() internally, which only
        # consumes rng.normal() draws if fading=="jakes" AND speed>=0.1 --
        # otherwise it returns 0.0 before drawing anything. The queue fed to
        # compute_sinr's shared rng must reflect that real consumption
        # pattern, or the shadow draw silently pulls the wrong value.
        jakes_will_draw = RAT_SPECS[rat]["fading"] == "jakes" and speed >= 0.1
        sinr_rng = FakeRng(standard_normals=([jz1, jz2, sz] if jakes_will_draw else [sz]))
        sinr_db = compute_sinr(rat, dist, speed, sinr_rng, mode=mode)

        link_rng = FakeRng(uniforms=[u])
        success = compute_link_success(rat, sinr_db, link_rng, mode=mode)

        print(f"{name}:")
        print(f"  path_loss_db      = {pl:.12f}")
        print(f"  jakes_fading_db   = {jakes_db:.12f}")
        print(f"  sinr_db           = {sinr_db:.12f}")
        print(f"  link_success      = {success}")
        print()


if __name__ == "__main__":
    main()
