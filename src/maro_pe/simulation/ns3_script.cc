#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/opengym-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("MaRopeNs3");

uint32_t g_n_vehicles = 4;
double g_simTime = 100.0;

Ptr<OpenGymSpace> MyGetObservationSpace(void)
{
  std::vector<uint32_t> shape = {g_n_vehicles, 12};
  std::string dtype = TypeNameGet<float> ();
  Ptr<OpenGymBoxSpace> space = CreateObject<OpenGymBoxSpace> (-1000.0, 1000.0, shape, dtype);
  return space;
}

Ptr<OpenGymSpace> MyGetActionSpace(void)
{
  std::vector<uint32_t> shape = {g_n_vehicles, 3}; // E.g., [RAT, ratio_a, ratio_b]
  std::string dtype = TypeNameGet<float> ();
  Ptr<OpenGymBoxSpace> space = CreateObject<OpenGymBoxSpace> (-1.0, 1.0, shape, dtype);
  return space;
}

bool MyGetGameOver(void)
{
  return (Simulator::Now().GetSeconds() >= g_simTime);
}

Ptr<OpenGymDataContainer> MyGetObservation(void)
{
  std::vector<uint32_t> shape = {g_n_vehicles, 12};
  Ptr<OpenGymBoxContainer<float> > box = CreateObject<OpenGymBoxContainer<float> >(shape);
  
  for (uint32_t i = 0; i < g_n_vehicles; i++) {
    for (uint32_t j = 0; j < 12; j++) {
      box->AddValue(0.0f); // Mock real physical state
    }
  }
  return box;
}

float MyGetReward(void)
{
  return -1.0;
}

std::string MyGetExtraInfo(void)
{
  return "";
}

bool MyExecuteActions(Ptr<OpenGymDataContainer> action)
{
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
  double envStepTime = 1.0;
  
  CommandLine cmd;
  cmd.AddValue ("openGymPort", "Port number for OpenGym env", openGymPort);
  cmd.AddValue ("n_vehicles", "Number of vehicles", g_n_vehicles);
  cmd.Parse (argc, argv);

  Ptr<OpenGymInterface> openGym = CreateObject<OpenGymInterface> (openGymPort);
  openGym->SetGetActionSpaceCb( MakeCallback (&MyGetActionSpace) );
  openGym->SetGetObservationSpaceCb( MakeCallback (&MyGetObservationSpace) );
  openGym->SetGetGameOverCb( MakeCallback (&MyGetGameOver) );
  openGym->SetGetObservationCb( MakeCallback (&MyGetObservation) );
  openGym->SetGetRewardCb( MakeCallback (&MyGetReward) );
  openGym->SetGetExtraInfoCb( MakeCallback (&MyGetExtraInfo) );
  openGym->SetExecuteActionsCb( MakeCallback (&MyExecuteActions) );
  
  NodeContainer ues;
  ues.Create(g_n_vehicles);
  
  MobilityHelper mobility;
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (ues);
  
  Simulator::Schedule (Seconds(0.0), &ScheduleNextStateRead, envStepTime, openGym);
  
  Simulator::Stop (Seconds (g_simTime));
  Simulator::Run ();
  
  openGym->NotifySimulationEnd();
  Simulator::Destroy ();
  return 0;
}
