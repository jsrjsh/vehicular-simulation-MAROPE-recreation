// v2x_environment.h
// Ported from env/environment.py

#ifndef MAROPE_V2X_ENVIRONMENT_H
#define MAROPE_V2X_ENVIRONMENT_H

#include <vector>
#include <map>
#include <string>
#include <memory>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <sstream>

#include "ns3/core-module.h"
#include "ns3/random-variable-stream.h"
#include "ns3/opengym-module.h"
#include "ns3/node-container.h"
#include "ns3/mobility-model.h"

#include "channel_model.h"

namespace marope {

constexpr double kCpuFreqHz = 2e9;
constexpr double kSafetyRemoteMecSpeedup = 1.5;
constexpr double kRemoteFactorBase = 0.5e-3;
constexpr double kDelayPerUnitMs = 50.0; // Baseline recreation default
constexpr double kRoadLengthM = 2600.0;
constexpr int kObsDim = 12;

struct ActionInfo {
  int rat_idx;
  double rho;
};

inline const ActionInfo& GetActionInfo(int action_idx) {
  static const ActionInfo kActionMap[11] = {
      {0, 0.00}, // 0
      {1, 0.25}, // 1
      {1, 0.50}, // 2
      {1, 0.75}, // 3
      {2, 0.25}, // 4
      {2, 0.50}, // 5
      {4, 0.25}, // 6
      {4, 0.50}, // 7
      {4, 1.00}, // 8
      {3, 0.50}, // 9
      {3, 1.00}  // 10
  };
  if (action_idx < 0 || action_idx > 10) {
    throw std::out_of_range("action_idx must be in [0,10]");
  }
  return kActionMap[action_idx];
}

struct TaskInfo {
  std::string type;
  double d_ms;
  double data_mb;
  double cpu_cycles;
  double alpha;
  double beta;
};

inline const TaskInfo& GetSafetyTask() {
  static const TaskInfo t = {"safety", 100.0, 0.1, 1e8, 0.70, 0.30};
  return t;
}
inline const TaskInfo& GetInfotainmentTask() {
  static const TaskInfo t = {"infotainment", 500.0, 2.0, 5e8, 0.40, 0.60};
  return t;
}
inline const TaskInfo& GetComputeTask() {
  static const TaskInfo t = {"compute", 1000.0, 5.0, 2e9, 0.20, 0.80};
  return t;
}

struct VehicleState {
  ns3::Vector pos;
  double speed;
  double battery;
  TaskInfo active_task;
  bool is_new_task;

  int tx_counters[5];
  int rx_counters[5];
  int rx_on_time_counters[5];
  
  // Last step stats for info dictionary
  double last_latency_ms;
  bool last_transmission_success;
  double last_adapted_rho;
  double last_u_otr;
  double last_u_prr;
  int last_chosen_rat;
  double last_chosen_rho;
};

struct RsuState {
  ns3::Vector pos;
  double queue_size;
  double cbr_prev;
  double cbr_curr;
};

class V2XEnvironment {
public:
  V2XEnvironment(int n_vehicles, int seed, ns3::NodeContainer* nodes) 
    : m_nVehicles(n_vehicles), m_totalOffloadTransmissions(0), m_episodeStep(0), m_nodes(nodes) {
    
    // Setup Random Variables
    m_uniformRv = ns3::CreateObject<ns3::UniformRandomVariable>();
    m_normalRv = ns3::CreateObject<ns3::NormalRandomVariable>();

    m_rsuStates.push_back({ns3::Vector(500.0, 0.0, 0.0), 0.0, 0.0, 0.0});
    m_rsuStates.push_back({ns3::Vector(1500.0, 0.0, 0.0), 0.0, 0.0, 0.0});

    m_vehicles.resize(m_nVehicles);
    Reset();
  }

  void Reset() {
    m_episodeStep = 0;
    m_totalOffloadTransmissions = 0;
    
    for (auto& rsu : m_rsuStates) {
      rsu.queue_size = 0.0;
      rsu.cbr_prev = 0.0;
      rsu.cbr_curr = 0.0;
    }

    for (int i = 0; i < m_nVehicles; ++i) {
      m_vehicles[i].battery = m_uniformRv->GetValue(70.0, 100.0);
      m_vehicles[i].active_task = SampleTask();
      m_vehicles[i].is_new_task = true;
      for (int r = 0; r < 5; ++r) {
        m_vehicles[i].tx_counters[r] = 0;
        m_vehicles[i].rx_counters[r] = 0;
        m_vehicles[i].rx_on_time_counters[r] = 0;
      }
    }
  }

  ns3::Ptr<ns3::OpenGymDataContainer> GetObservation() {
    std::vector<uint32_t> shape = {(uint32_t)m_nVehicles, kObsDim};
    ns3::Ptr<ns3::OpenGymBoxContainer<float>> box = ns3::CreateObject<ns3::OpenGymBoxContainer<float>>(shape);
    
    for (int i = 0; i < m_nVehicles; ++i) {
      if (m_nodes && i < (int)m_nodes->GetN()) {
        ns3::Ptr<ns3::MobilityModel> mob = m_nodes->Get(i)->GetObject<ns3::MobilityModel>();
        if (mob) {
          m_vehicles[i].pos = mob->GetPosition();
          ns3::Vector vel = mob->GetVelocity();
          m_vehicles[i].speed = std::sqrt(vel.x * vel.x + vel.y * vel.y + vel.z * vel.z);
        }
      }
      ns3::Vector pos = m_vehicles[i].pos;
      int rsu_idx = GetNearestRsu(pos);
      double dist = ns3::CalculateDistance(pos, m_rsuStates[rsu_idx].pos);
      double speed = m_vehicles[i].speed;

      // 1. SINRs
      for (int r = 1; r < 5; ++r) {
        double shadow_z = m_normalRv->GetValue(0.0, 1.0);
        double jakes_z1 = m_normalRv->GetValue(0.0, 1.0);
        double jakes_z2 = m_normalRv->GetValue(0.0, 1.0);
        double sinr_db = ComputeSinrDb(r, dist, speed, shadow_z, jakes_z1, jakes_z2, Mode::kBaselineRecreation);
        
        float val = std::max(0.0, std::min(1.0, (sinr_db + 20.0) / 60.0));
        box->AddValue(val);
      }

      // 2. PRRs
      for (int r = 1; r < 5; ++r) {
        box->AddValue((float)GetEmpiricalPrr(i, r));
      }

      // 3. Queue Size
      box->AddValue((float)std::max(0.0, std::min(1.0, m_rsuStates[rsu_idx].queue_size / m_nVehicles)));

      // 4. Data Size
      box->AddValue((float)(m_vehicles[i].active_task.data_mb / 5.0));

      // 5. Deadline
      box->AddValue((float)(m_vehicles[i].active_task.d_ms / 2000.0));

      // 6. Battery
      box->AddValue((float)(m_vehicles[i].battery / 100.0));
    }
    return box;
  }

  void ExecuteActions(ns3::Ptr<ns3::OpenGymDataContainer> action_container, std::vector<float>& out_rewards) {
    m_episodeStep++;
    out_rewards.resize(m_nVehicles, 0.0f);
    
    ns3::Ptr<ns3::OpenGymDiscreteContainer> discrete_actions = ns3::DynamicCast<ns3::OpenGymDiscreteContainer>(action_container);

    std::vector<int> actions(m_nVehicles, 0);
    // gym env sends a dict of Discrete(11). This manifests in OpenGym as a DiscreteContainer or BoxContainer.
    // In ns3_script.cc, action space was BoxSpace[n_vehicles, 3]. We need to change that to Discrete or Box[n_vehicles].
    // Since ns3gym might receive it as BoxContainer if we specify BoxSpace:
    ns3::Ptr<ns3::OpenGymBoxContainer<float>> box_actions = ns3::DynamicCast<ns3::OpenGymBoxContainer<float>>(action_container);
    if (box_actions) {
      for (int i = 0; i < m_nVehicles; ++i) {
        actions[i] = (int)box_actions->GetValue(i);
      }
    }

    // 1. Decode actions and update RSU queues
    std::vector<ActionInfo> decoded_actions(m_nVehicles);
    std::vector<double> rsu_workloads(m_rsuStates.size(), 0.0);

    for (int i = 0; i < m_nVehicles; ++i) {
      decoded_actions[i] = GetActionInfo(actions[i]);
      int rsu_idx = GetNearestRsu(m_vehicles[i].pos);
      if (decoded_actions[i].rat_idx > 0 && decoded_actions[i].rho > 0.0) {
        rsu_workloads[rsu_idx] += decoded_actions[i].rho;
      }
    }

    for (size_t r = 0; r < m_rsuStates.size(); ++r) {
      m_rsuStates[r].queue_size = rsu_workloads[r];
      m_rsuStates[r].cbr_prev = m_rsuStates[r].cbr_curr;
      m_rsuStates[r].cbr_curr = std::max(0.0, std::min(1.0, m_rsuStates[r].queue_size / m_nVehicles));
    }

    // 2. Compute SINRs and adapt rhos
    std::vector<double> adapted_rhos(m_nVehicles, 0.0);
    std::vector<std::vector<double>> sinrs(m_nVehicles, std::vector<double>(5, 0.0));
    
    for (int i = 0; i < m_nVehicles; ++i) {
      if (m_nodes && i < (int)m_nodes->GetN()) {
        ns3::Ptr<ns3::MobilityModel> mob = m_nodes->Get(i)->GetObject<ns3::MobilityModel>();
        if (mob) {
          m_vehicles[i].pos = mob->GetPosition();
          ns3::Vector vel = mob->GetVelocity();
          m_vehicles[i].speed = std::sqrt(vel.x * vel.x + vel.y * vel.y + vel.z * vel.z);
        }
      }
      int rat_idx = decoded_actions[i].rat_idx;
      double rho = decoded_actions[i].rho;
      double dist = ns3::CalculateDistance(m_vehicles[i].pos, m_rsuStates[GetNearestRsu(m_vehicles[i].pos)].pos);
      double speed = m_vehicles[i].speed;

      for (int r = 1; r < 5; ++r) {
        double shadow_z = m_normalRv->GetValue(0.0, 1.0);
        double jakes_z1 = m_normalRv->GetValue(0.0, 1.0);
        double jakes_z2 = m_normalRv->GetValue(0.0, 1.0);
        sinrs[i][r] = ComputeSinrDb(r, dist, speed, shadow_z, jakes_z1, jakes_z2, Mode::kBaselineRecreation);
      }

      if (rat_idx == 0 || rho == 0.0) {
        adapted_rhos[i] = 0.0;
      } else {
        double sum_gammas = 0.0;
        for(int r = 1; r < 5; ++r) sum_gammas += std::max(std::pow(10.0, sinrs[i][r] / 10.0), 1e-6);
        double q_r = std::max(std::pow(10.0, sinrs[i][rat_idx] / 10.0), 1e-6) / sum_gammas;
        adapted_rhos[i] = std::max(0.0, std::min(1.0, rho * q_r));
      }
    }

    // 3. Compute Latency (Energy is OMITTED)
    std::vector<double> latencies(m_nVehicles, 0.0);
    for (int i = 0; i < m_nVehicles; ++i) {
      int rat_idx = decoded_actions[i].rat_idx;
      double rho_prime = adapted_rhos[i];
      const TaskInfo& task = m_vehicles[i].active_task;
      
      double l_local = (task.cpu_cycles / kCpuFreqHz) * 1000.0;
      
      if (rat_idx == 0 || rho_prime == 0.0) {
        latencies[i] = l_local;
      } else {
        double remote_speed = (task.type == "safety") ? kSafetyRemoteMecSpeedup : 1.0;
        double remote_factor = kRemoteFactorBase / remote_speed;
        double l_remote = (task.data_mb * rho_prime * remote_factor) * 1000.0;
        
        int rsu_idx = GetNearestRsu(m_vehicles[i].pos);
        double l_queue = m_rsuStates[rsu_idx].queue_size * kDelayPerUnitMs;
        
        // Patched: use linear formula instead of log10 to fix the compression bug
        double l_local_term = l_local * (1.0 - rho_prime);
        latencies[i] = std::max(l_local_term, l_remote + l_queue + GetRatSpec(rat_idx).latency_ms);
      }
    }

    // 4. Bernoulli Success
    std::vector<bool> successes(m_nVehicles, true);
    for (int i = 0; i < m_nVehicles; ++i) {
      int rat_idx = decoded_actions[i].rat_idx;
      if (rat_idx > 0 && adapted_rhos[i] > 0.0) {
        double u = m_uniformRv->GetValue(0.0, 1.0);
        auto res = ComputeLinkSuccess(rat_idx, sinrs[i][rat_idx], u, Mode::kBaselineRecreation);
        successes[i] = res.success;

        m_vehicles[i].tx_counters[rat_idx]++;
        m_totalOffloadTransmissions++;
        if (res.success) {
          m_vehicles[i].rx_counters[rat_idx]++;
          if (latencies[i] <= m_vehicles[i].active_task.d_ms) {
            m_vehicles[i].rx_on_time_counters[rat_idx]++;
          }
        }
      }
      
      m_vehicles[i].last_latency_ms = latencies[i];
      m_vehicles[i].last_transmission_success = successes[i];
      m_vehicles[i].last_adapted_rho = adapted_rhos[i];
      m_vehicles[i].last_chosen_rat = decoded_actions[i].rat_idx;
      m_vehicles[i].last_chosen_rho = decoded_actions[i].rho;
    }

    // 5. Compute rewards
    for (int i = 0; i < m_nVehicles; ++i) {
      int rat_idx = decoded_actions[i].rat_idx;
      double prr_val = (rat_idx == 0 || adapted_rhos[i] == 0.0) ? 1.0 : GetEmpiricalPrr(i, rat_idx);
      double otr_val = (rat_idx == 0 || adapted_rhos[i] == 0.0) ? 0.0 : GetEmpiricalOtr(i, rat_idx);
      
      int rsu_idx = GetNearestRsu(m_vehicles[i].pos);
      double delta_cbr = std::max(-0.5, std::min(0.5, m_rsuStates[rsu_idx].cbr_prev - m_rsuStates[rsu_idx].cbr_curr));

      const TaskInfo& task = m_vehicles[i].active_task;
      double l_ratio = std::max(-100.0, std::min(100.0, latencies[i] / task.d_ms));
      double e_ratio = 0.0; // OMITTED ENERGY

      double u = task.alpha * otr_val
               + (task.beta / 2.0) * std::exp(-l_ratio)
               + (task.beta / 2.0) * std::exp(-e_ratio)
               + (task.beta / 4.0) * delta_cbr;
      
      double u_prr_val = task.alpha * prr_val
                       + (task.beta / 2.0) * std::exp(-l_ratio)
                       + (task.beta / 2.0) * std::exp(-e_ratio)
                       + (task.beta / 4.0) * delta_cbr;

      out_rewards[i] = (float)std::max(0.0, std::min(1.0, u));
      m_vehicles[i].last_u_otr = out_rewards[i]; // Roughly the same logic for info dict
      m_vehicles[i].last_u_prr = (double)std::max(0.0, std::min(1.0, u_prr_val));
    }

    // 6. Update Mobility (removed, handled by ns-3 Ns2MobilityHelper)

    // 7. Task Resampling
    for (int i = 0; i < m_nVehicles; ++i) {
      if (m_uniformRv->GetValue(0.0, 1.0) < 0.3) {
        m_vehicles[i].active_task = SampleTask();
        m_vehicles[i].is_new_task = true;
      } else {
        m_vehicles[i].is_new_task = false;
      }
    }
  }

  std::string BuildExtraInfo() {
    std::ostringstream oss;
    oss << "{";
    for (int i = 0; i < m_nVehicles; ++i) {
      if (i > 0) oss << ", ";
      oss << "\"" << i << "\": {";
      oss << "\"latency_ms\": " << m_vehicles[i].last_latency_ms << ", ";
      oss << "\"energy_j\": 0.0, ";
      oss << "\"transmission_success\": " << (m_vehicles[i].last_transmission_success ? "true" : "false") << ", ";
      oss << "\"task_type\": \"" << m_vehicles[i].active_task.type << "\", ";
      oss << "\"chosen_rat\": " << m_vehicles[i].last_chosen_rat << ", ";
      oss << "\"chosen_rho\": " << m_vehicles[i].last_chosen_rho << ", ";
      oss << "\"adapted_rho\": " << m_vehicles[i].last_adapted_rho << ", ";
      oss << "\"u_otr\": " << m_vehicles[i].last_u_otr << ", ";
      oss << "\"u_prr\": " << m_vehicles[i].last_u_prr << ", ";
      double prr = (m_vehicles[i].last_chosen_rat > 0) ? GetEmpiricalPrr(i, m_vehicles[i].last_chosen_rat) : 1.0;
      oss << "\"empirical_prr\": " << prr << ", ";
      int rsu_idx = GetNearestRsu(m_vehicles[i].pos);
      double queue_delay_ms = m_rsuStates[rsu_idx].queue_size * kDelayPerUnitMs;
      oss << "\"queue_delay_ms\": " << queue_delay_ms << ", ";
      oss << "\"policy_type\": \"learned\"";
      oss << "}";
    }
    oss << "}";
    return oss.str();
  }

  bool IsGameOver(double simTime) const {
    return (m_episodeStep >= 200); // DEFAULT_MAX_STEPS = 200
  }

private:
  int GetNearestRsu(ns3::Vector pos) const {
    double min_dist = 1e9;
    int nearest = 0;
    for (size_t i = 0; i < m_rsuStates.size(); ++i) {
      double dist = ns3::CalculateDistance(pos, m_rsuStates[i].pos);
      if (dist < min_dist) {
        min_dist = dist;
        nearest = i;
      }
    }
    return nearest;
  }

  TaskInfo SampleTask() {
    double u = m_uniformRv->GetValue(0.0, 1.0);
    // URLLC scenario mix: 0.65 Safety, 0.20 Infotainment, 0.15 Compute
    if (u < 0.65) return GetSafetyTask();
    if (u < 0.85) return GetInfotainmentTask();
    return GetComputeTask();
  }

  double GetEmpiricalPrr(int vehicle_idx, int rat_idx) const {
    const auto& v = m_vehicles[vehicle_idx];
    if (v.tx_counters[rat_idx] > 0) {
      return (double)v.rx_counters[rat_idx] / v.tx_counters[rat_idx];
    } else {
      return (m_totalOffloadTransmissions > 0) ? 0.5 : 1.0;
    }
  }

  double GetEmpiricalOtr(int vehicle_idx, int rat_idx) const {
    const auto& v = m_vehicles[vehicle_idx];
    if (v.tx_counters[rat_idx] > 0) {
      return (double)v.rx_on_time_counters[rat_idx] / v.tx_counters[rat_idx];
    } else {
      return (m_totalOffloadTransmissions > 0) ? 0.5 : 1.0;
    }
  }

  int m_nVehicles;
  int m_totalOffloadTransmissions;
  int m_episodeStep;
  
  std::vector<VehicleState> m_vehicles;
  std::vector<RsuState> m_rsuStates;
  ns3::NodeContainer* m_nodes;

  ns3::Ptr<ns3::UniformRandomVariable> m_uniformRv;
  ns3::Ptr<ns3::NormalRandomVariable> m_normalRv;
};

} // namespace marope

#endif // MAROPE_V2X_ENVIRONMENT_H
