// channel_model.h
//
// Line-for-line C++ translation of env/channel.py + the channel-relevant
// fields of env/config.py::RAT_SPECS, for use inside ns-3 (ns3_script.cc)
// or standalone (see channel_model_golden_test.cc).
//
// SCOPE: this is the physical-layer channel model ONLY (path loss, Jakes
// fading, SINR, link-success probability). It does NOT include the energy
// model. env/environment.py's implemented energy formula
// (P_CPU_W * log10(c_ratio)) is mathematically invalid -- it returns
// negative energy by construction for the common case -- and was removed
// from the paper entirely (see _claude_workspace/ENERGY_METRIC_DECISION.md).
// Porting a formula already known to be broken would just reproduce the bug
// in a second language. Energy is intentionally out of scope here; if it's
// ever wanted, that's new work requiring its own formula design and
// sign-off, not a translation task.
//
// MODE: env/channel.py supports two modes with materially different
// formulas ("physically_corrected" vs "baseline_recreation"/"legacy_guide").
// v25's validated numbers (CAMPAIGN_CORRECTED_20260803) were produced
// exclusively under env_mode="baseline_recreation" (see
// _claude_workspace/scripts/run_corrected_campaign.py: ENV_MODE =
// "baseline_recreation"). Both modes are implemented below for fidelity to
// the Python source, but BASELINE_RECREATION is what must be used for any
// comparison against v25 -- using PHYSICALLY_CORRECTED here would compare
// against a model that never actually produced any of the paper's numbers.
//
// RANDOMNESS: numpy's RandomState and C++'s standard library RNGs do not
// produce bit-identical output for "the same seed" -- their underlying
// algorithms differ enough (even both being Mersenne Twister variants)
// that matching them exactly would require reimplementing numpy's exact
// generator in C++, which is not worth doing. Instead, every function here
// takes its random draws as explicit parameters (dependency injection)
// rather than drawing internally. This makes the *formula* -- the actual
// translation risk -- independently verifiable against known Python output
// (see channel_model_golden_test.cc + scripts/compute_channel_model_golden_values.py),
// without needing cross-language RNG equivalence at all. Production use
// (wiring this into ns3_script.cc's OpenGym callbacks) should draw z1, z2,
// shadow_z, and u from ns-3's own RNG (ns3::NormalRandomVariable /
// UniformRandomVariable) at the call site.

#ifndef MAROPE_CHANNEL_MODEL_H
#define MAROPE_CHANNEL_MODEL_H

#include <algorithm>
#include <cassert>
#include <cmath>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>

namespace marope {

constexpr double kSpeedOfLightMps = 3e8;  // matches env/channel.py SPEED_OF_LIGHT

enum class Mode { kBaselineRecreation, kPhysicallyCorrected };

enum class Fading { kNone, kJakes, kConstant };

enum class PathLossModel { kNone, k3gppV2x, k5gUmi, kWifiAx };

// Mirrors env/config.py::RAT_SPECS -- only the channel-relevant fields.
// RAT index convention matches the Python source exactly:
// 0=Local, 1=LTE, 2=ITS-G5, 3=WiFi-6, 4=5G-NR.
struct RatSpec {
  const char* name;
  double noise_dbm;         // NaN for Local (unused -- Local bypasses the channel model)
  double shadow_sigma_db;
  double sinr_thresh_db;
  Fading fading;
  double freq_ghz;
  double tx_power_dbm;
  PathLossModel path_loss_model;
};

// clang-format off
inline const RatSpec& GetRatSpec(int rat_idx) {
  static const RatSpec kSpecs[5] = {
      /* 0 Local  */ {"Local", 0.0, 0.0, 0.0, Fading::kNone, 0.0, 0.0, PathLossModel::kNone},
      /* 1 LTE    */ {"LTE",   -110.0, 4.0, 4.0, Fading::kJakes,    1.8, 23.0, PathLossModel::k3gppV2x},
      /* 2 ITS_G5 */ {"ITS_G5",-90.0,  4.0, 4.0, Fading::kConstant, 5.9, 23.0, PathLossModel::k3gppV2x},
      /* 3 WiFi6  */ {"WiFi6", -90.0,  3.0, 5.0, Fading::kConstant, 5.0, 20.0, PathLossModel::kWifiAx},
      /* 4 5GNR   */ {"5GNR",  -110.0, 4.0, 4.0, Fading::kJakes,    3.5, 23.0, PathLossModel::k5gUmi},
  };
  // clang-format on
  if (rat_idx < 0 || rat_idx > 4) {
    throw std::out_of_range("rat_idx must be in [0,4]");
  }
  return kSpecs[rat_idx];
}

// Direct translation of compute_path_loss(). Fully deterministic (no
// randomness), so this is the one function that can be golden-tested for
// an EXACT numeric match against Python, not just formula-equivalence.
inline double ComputePathLossDb(int rat_idx, double distance_m) {
  const double d = std::max(distance_m, 1.0);
  const RatSpec& spec = GetRatSpec(rat_idx);

  switch (spec.path_loss_model) {
    case PathLossModel::k3gppV2x:
      return 47.9 + 10.0 * std::log10(d / 10.0);
    case PathLossModel::k5gUmi:
      return 32.4 + 20.0 * std::log10(spec.freq_ghz) + 20.0 * std::log10(d);
    case PathLossModel::kWifiAx:
      return 40.05 + 20.0 * std::log10(spec.freq_ghz / 2.4) + 20.0 * std::log10(d);
    case PathLossModel::kNone:
      return 0.0;
  }
  throw std::logic_error("unreachable: unhandled PathLossModel");
}

// Direct translation of compute_jakes_fading(). z1, z2 are pre-drawn
// standard-normal (mean 0, std 1) samples -- caller-supplied, matching the
// two rng.normal(0.0, 1.0) calls in the Python source. Only active for
// Fading::kJakes RATs (LTE, 5G-NR); returns 0.0 otherwise, matching Python.
inline double ComputeJakesFadingDb(int rat_idx, double speed_mps, double z1, double z2,
                                    Mode mode = Mode::kBaselineRecreation) {
  const RatSpec& spec = GetRatSpec(rat_idx);
  if (spec.fading != Fading::kJakes) {
    return 0.0;
  }
  if (speed_mps < 0.1) {
    return 0.0;
  }

  const double freq_ghz = spec.freq_ghz;
  double f_d;
  if (mode == Mode::kBaselineRecreation) {
    // Literal unscaled formula -- freq_ghz used as-is, NOT converted to Hz.
    // This is what produced v25's numbers. Do not "fix" this to the
    // physically-corrected formula below without an explicit decision to
    // regenerate the whole campaign -- see file header.
    f_d = (speed_mps * freq_ghz) / kSpeedOfLightMps;
  } else {
    // physically_corrected: freq_ghz -> Hz
    f_d = (speed_mps * (freq_ghz * 1e9)) / kSpeedOfLightMps;
  }

  const double t_c = 0.423 / std::max(f_d, 1e-6);
  const double delta_t = 0.1;
  const double r = std::min(delta_t / t_c, 10.0);

  // Rayleigh fading envelope A from two independent standard normals.
  const double a = std::max(std::sqrt(z1 * z1 + z2 * z2), 1e-9);

  const double l_fade = (-20.0 * std::log10(a)) * std::min(r / 5.0, 1.5);
  return std::max(l_fade, 0.0);
}

// Direct translation of compute_sinr(). shadow_z, jakes_z1, jakes_z2 are
// pre-drawn standard-normal samples (see file header on randomness).
// Returns +infinity for Local, matching Python's float("inf").
inline double ComputeSinrDb(int rat_idx, double distance_m, double speed_mps, double shadow_z,
                             double jakes_z1, double jakes_z2,
                             Mode mode = Mode::kBaselineRecreation) {
  const RatSpec& spec = GetRatSpec(rat_idx);
  if (rat_idx == 0) {  // Local
    return std::numeric_limits<double>::infinity();
  }

  const double p_tx = spec.tx_power_dbm;
  const double n_0 = spec.noise_dbm;
  const double sigma_h = spec.shadow_sigma_db;

  const double pl = ComputePathLossDb(rat_idx, distance_m);
  const double l_fade = ComputeJakesFadingDb(rat_idx, speed_mps, jakes_z1, jakes_z2, mode);

  // Shadow fading: Python's rng.normal(0.0, sigma_h) == sigma_h * standard_normal().
  const double raw_shadow = sigma_h * shadow_z;
  double x_shadow;
  if (mode == Mode::kBaselineRecreation) {
    // Literal formula from the recreation guide: shadowing enters SQUARED.
    // This is what produced v25's numbers -- not a bug to "fix" here.
    x_shadow = raw_shadow * raw_shadow;
  } else {
    x_shadow = raw_shadow;
  }

  return p_tx - pl - n_0 + x_shadow - l_fade;
}

struct LinkSuccessResult {
  bool success;
  double probability;  // exposed for testing -- Python doesn't return this,
                        // but golden-testing the probability separately from
                        // the Bernoulli draw isolates the formula from the
                        // random comparison.
};

// Direct translation of compute_link_success(). `u` is a pre-drawn
// Uniform(0,1) sample (replaces rng.uniform(0.0, 1.0) < p). Always succeeds
// for Local, matching Python's unconditional `return True`.
inline LinkSuccessResult ComputeLinkSuccess(int rat_idx, double sinr_db, double u,
                                             Mode mode = Mode::kBaselineRecreation) {
  (void)mode;  // link-success formula does not vary by mode in the Python source
  const RatSpec& spec = GetRatSpec(rat_idx);
  if (rat_idx == 0) {  // Local
    return {true, 1.0};
  }

  const double tau = spec.sinr_thresh_db;
  const double sigma_h = spec.shadow_sigma_db;

  double exponent = -(sinr_db - tau) / (3.0 * sigma_h);
  // Clip to avoid overflow in exp(), matching Python's explicit clamp.
  exponent = std::max(std::min(exponent, 100.0), -100.0);
  const double p = 1.0 / (1.0 + std::exp(exponent));

  assert(p >= 0.0 && p <= 1.0);  // boundary assertion -- see NS3_SUMO_STATUS.md
                                  // "next steps" on why this matters
  return {u < p, p};
}

}  // namespace marope

#endif  // MAROPE_CHANNEL_MODEL_H
