#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/opengym-module.h"
#include "ns3/ns2-mobility-helper.h"

#include "v2x_environment.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("MaRopeNs3");

uint32_t g_n_vehicles = 4;
double g_simTime = 100.0;
marope::V2XEnvironment* g_v2xEnv = nullptr;
std::vector<float> g_lastRewards;

Ptr<OpenGymSpace> MyGetObservationSpace(void)
{
  std::vector<uint32_t> shape = {g_n_vehicles, marope::kObsDim};
  std::string dtype = TypeNameGet<float> ();
  Ptr<OpenGymBoxSpace> space = CreateObject<OpenGymBoxSpace> (0.0, 1.0, shape, dtype);
  return space;
}

Ptr<OpenGymSpace> MyGetActionSpace(void)
{
  // Python gym env uses Dict(Discrete(11)). ns3gym doesn't support Dict directly.
  // The python wrapper ns3_sumo_env.py encodes this as a list of integers if we use BoxSpace, 
  // or a BoxSpace. Let's match BoxSpace(0, 10, shape=(g_n_vehicles,))
  std::vector<uint32_t> shape = {g_n_vehicles};
  std::string dtype = TypeNameGet<float> ();
  Ptr<OpenGymBoxSpace> space = CreateObject<OpenGymBoxSpace> (0.0, 10.0, shape, dtype);
  return space;
}

bool MyGetGameOver(void)
{
  if (g_v2xEnv) {
    return g_v2xEnv->IsGameOver(Simulator::Now().GetSeconds());
  }
  return (Simulator::Now().GetSeconds() >= g_simTime);
}

Ptr<OpenGymDataContainer> MyGetObservation(void)
{
  if (g_v2xEnv) {
    return g_v2xEnv->GetObservation();
  }
  
  std::vector<uint32_t> shape = {g_n_vehicles, marope::kObsDim};
  Ptr<OpenGymBoxContainer<float> > box = CreateObject<OpenGymBoxContainer<float> >(shape);
  for (uint32_t i = 0; i < g_n_vehicles; i++) {
    for (uint32_t j = 0; j < marope::kObsDim; j++) {
      box->AddValue(0.0f);
    }
  }
  return box;
}

float MyGetReward(void)
{
  // In multi-agent, we might return sum or mean.
  // Actually, ns3gym only expects a single float for reward in the C++ signature,
  // while python might need a Dict. ns3_sumo_env.py's step function currently overwrites it:
  // rewards = {i: -1.0 for i in self.agents}
  // So returning 0.0 is fine for now; we'll update python to read from info if needed,
  // or just let it return 0.0 since rewards are generated in C++ and stored.
  return 0.0f; 
}

std::string MyGetExtraInfo(void)
{
  if (g_v2xEnv) {
    return g_v2xEnv->BuildExtraInfo();
  }
  return "";
}

bool MyExecuteActions(Ptr<OpenGymDataContainer> action)
{
  if (g_v2xEnv) {
    g_v2xEnv->ExecuteActions(action, g_lastRewards);
  }
  return true;
}

void ScheduleNextStateRead(double envStepTime, Ptr<OpenGymInterface> openGym)
{
  Simulator::Schedule (Seconds(envStepTime), &ScheduleNextStateRead, envStepTime, openGym);
  openGym->NotifyCurrentState();
}

int main(int argc, char *argv[])
{
  uint32_t openGymPort = 5555;
  double envStepTime = 0.1; // 10Hz stepping in V2XEnv
  std::string traceFile = "";
  
  uint32_t simSeed = 1;
  CommandLine cmd;
  cmd.AddValue ("openGymPort", "Port number for OpenGym env", openGymPort);
  cmd.AddValue ("simSeed", "Simulation seed", simSeed);
  cmd.AddValue ("n_vehicles", "Number of vehicles", g_n_vehicles);
  cmd.AddValue ("traceFile", "ns2 mobility trace file", traceFile);
  cmd.Parse (argc, argv);

  ns3::RngSeedManager::SetSeed(simSeed);

  NodeContainer ues;
  ues.Create(g_n_vehicles);

  g_v2xEnv = new marope::V2XEnvironment(g_n_vehicles, simSeed, &ues);

  Ptr<OpenGymInterface> openGym = CreateObject<OpenGymInterface> (openGymPort);
  openGym->SetGetActionSpaceCb( MakeCallback (&MyGetActionSpace) );
  openGym->SetGetObservationSpaceCb( MakeCallback (&MyGetObservationSpace) );
  openGym->SetGetGameOverCb( MakeCallback (&MyGetGameOver) );
  openGym->SetGetObservationCb( MakeCallback (&MyGetObservation) );
  openGym->SetGetRewardCb( MakeCallback (&MyGetReward) );
  openGym->SetGetExtraInfoCb( MakeCallback (&MyGetExtraInfo) );
  openGym->SetExecuteActionsCb( MakeCallback (&MyExecuteActions) );
  
  if (traceFile != "") {
    Ns2MobilityHelper ns2 = Ns2MobilityHelper (traceFile);
    ns2.Install ();
  } else {
    MobilityHelper mobility;
    mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
    mobility.Install (ues);
  }
  
  Simulator::Schedule (Seconds(0.0), &ScheduleNextStateRead, envStepTime, openGym);
  
  Simulator::Stop (Seconds (g_simTime));
  Simulator::Run ();
  
  openGym->NotifySimulationEnd();
  Simulator::Destroy ();
  
  delete g_v2xEnv;
  return 0;
}
