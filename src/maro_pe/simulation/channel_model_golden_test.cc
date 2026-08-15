// channel_model_golden_test.cc
//
// Standalone C++ test (no ns-3 dependency) verifying channel_model.h's
// translation against golden values computed from the real Python
// env/channel.py (see scripts/compute_channel_model_golden_values.py --
// run that script and diff its output against this test's PASS/FAIL lines
// if you change either side; the two files must stay in sync by hand,
// there is no automated cross-language test runner here).
//
// Build (no ns-3 needed):
//   g++ -std=c++17 -O2 channel_model_golden_test.cc -o channel_model_golden_test
//   ./channel_model_golden_test

#include <cmath>
#include <cstdio>

#include "channel_model.h"

using marope::ComputeJakesFadingDb;
using marope::ComputeLinkSuccess;
using marope::ComputePathLossDb;
using marope::ComputeSinrDb;
using marope::Mode;

namespace {

int g_failures = 0;

void ExpectNear(const char* label, double actual, double expected, double tol = 1e-9) {
  const double diff = std::fabs(actual - expected);
  if (diff > tol) {
    std::printf("  FAIL %-20s actual=%.12f expected=%.12f diff=%.3e\n", label, actual, expected,
                diff);
    g_failures++;
  } else {
    std::printf("  ok   %-20s %.12f\n", label, actual);
  }
}

void ExpectBool(const char* label, bool actual, bool expected) {
  if (actual != expected) {
    std::printf("  FAIL %-20s actual=%s expected=%s\n", label, actual ? "true" : "false",
                expected ? "true" : "false");
    g_failures++;
  } else {
    std::printf("  ok   %-20s %s\n", label, actual ? "true" : "false");
  }
}

}  // namespace

int main() {
  // Values below are copied from `python3 scripts/compute_channel_model_golden_values.py`
  // (run 2026-08-15). Re-run that script and update here if channel_model.h
  // or env/channel.py ever change.

  {
    std::printf("lte_300m_20mps_baseline:\n");
    const int rat = 1;
    const double dist = 300.0, speed = 20.0;
    const double jz1 = 0.8, jz2 = -0.3, sz = 0.5, u = 0.4;
    ExpectNear("path_loss_db", ComputePathLossDb(rat, dist), 62.671212547197);
    ExpectNear("jakes_fading_db",
               ComputeJakesFadingDb(rat, speed, jz1, jz2, Mode::kBaselineRecreation),
               0.000000064623, 1e-9);
    const double sinr = ComputeSinrDb(rat, dist, speed, sz, jz1, jz2, Mode::kBaselineRecreation);
    ExpectNear("sinr_db", sinr, 74.328787388181);
    ExpectBool("link_success", ComputeLinkSuccess(rat, sinr, u, Mode::kBaselineRecreation).success,
               true);
  }

  {
    std::printf("wifi6_50m_0mps_baseline:\n");
    const int rat = 3;
    const double dist = 50.0, speed = 0.0;
    const double jz1 = 0.0, jz2 = 0.0, sz = -0.7, u = 0.9;
    ExpectNear("path_loss_db", ComputePathLossDb(rat, dist), 80.404575339209);
    ExpectNear("jakes_fading_db",
               ComputeJakesFadingDb(rat, speed, jz1, jz2, Mode::kBaselineRecreation), 0.0);
    const double sinr = ComputeSinrDb(rat, dist, speed, sz, jz1, jz2, Mode::kBaselineRecreation);
    ExpectNear("sinr_db", sinr, 34.005424660791);
    ExpectBool("link_success", ComputeLinkSuccess(rat, sinr, u, Mode::kBaselineRecreation).success,
               true);
  }

  {
    std::printf("5gnr_800m_30mps_baseline:\n");
    const int rat = 4;
    const double dist = 800.0, speed = 30.0;
    const double jz1 = -1.2, jz2 = 0.6, sz = 1.1, u = 0.1;
    ExpectNear("path_loss_db", ComputePathLossDb(rat, dist), 101.343160626844);
    const double sinr = ComputeSinrDb(rat, dist, speed, sz, jz1, jz2, Mode::kBaselineRecreation);
    ExpectNear("sinr_db", sinr, 51.016839373156);
    ExpectBool("link_success", ComputeLinkSuccess(rat, sinr, u, Mode::kBaselineRecreation).success,
               true);
  }

  {
    std::printf("itsg5_150m_15mps_baseline:\n");
    const int rat = 2;
    const double dist = 150.0, speed = 15.0;
    const double jz1 = 0.3, jz2 = 0.3, sz = -0.2, u = 0.6;
    ExpectNear("path_loss_db", ComputePathLossDb(rat, dist), 59.660912590557);
    const double sinr = ComputeSinrDb(rat, dist, speed, sz, jz1, jz2, Mode::kBaselineRecreation);
    ExpectNear("sinr_db", sinr, 53.979087409443);
    ExpectBool("link_success", ComputeLinkSuccess(rat, sinr, u, Mode::kBaselineRecreation).success,
               true);
  }

  {
    // Same inputs as test 1, but physically_corrected mode -- exercises the
    // other branch (Hz-scaled Jakes frequency, unsquared shadowing).
    std::printf("lte_300m_20mps_corrected:\n");
    const int rat = 1;
    const double dist = 300.0, speed = 20.0;
    const double jz1 = 0.8, jz2 = -0.3, sz = 0.5, u = 0.4;
    ExpectNear("path_loss_db", ComputePathLossDb(rat, dist), 62.671212547197);
    ExpectNear("jakes_fading_db",
               ComputeJakesFadingDb(rat, speed, jz1, jz2, Mode::kPhysicallyCorrected),
               2.050157098193);
    const double sinr =
        ComputeSinrDb(rat, dist, speed, sz, jz1, jz2, Mode::kPhysicallyCorrected);
    ExpectNear("sinr_db", sinr, 70.278630354610);
    ExpectBool("link_success",
               ComputeLinkSuccess(rat, sinr, u, Mode::kPhysicallyCorrected).success, true);
  }

  std::printf("\n%s (%d failures)\n", g_failures == 0 ? "ALL PASS" : "SOME FAILED", g_failures);
  return g_failures == 0 ? 0 : 1;
}
