/* export PATH=~/installed/gazebo_debug/bin:$PATH
export LD_LIBRARY_PATH=~/installed/gazebo_debug/lib

* Copyright (C) 2017 Vrije Universiteit Amsterdam
*
* Licensed under the Apache License, Version 2.0 (the "License");
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
* Author: Elte Hupkes
* Date: May 3, 2015
*
*/

#include  <stdexcept>

#include <gazebo/sensors/sensors.hh>

#include <revolve/gazebo/motors/MotorFactory.h>
#include <revolve/gazebo/sensors/SensorFactory.h>
#include <revolve/gazebo/brains/Brains.h>
#include <revolve/gazebo/brains/DifferentialCPGClean.h>

#include "RobotController.h"

namespace gz = gazebo;

using namespace revolve::gazebo;

/////////////////////////////////////////////////
/// Default actuation time is given and this will be overwritten by the plugin
/// config in Load.
RobotController::RobotController()
    : actuationTime_(0)
{
}

/////////////////////////////////////////////////
RobotController::~RobotController()
{
  this->node_.reset();
  this->world_.reset();
  this->motorFactory_.reset();
  this->sensorFactory_.reset();
}

/////////////////////////////////////////////////
void RobotController::Load(
    ::gazebo::physics::ModelPtr _parent,
    sdf::ElementPtr _sdf)
{
  // Store the pointer to the model / world
  this->model_ = _parent;
  this->world_ = _parent->GetWorld();
  this->initTime_ = this->world_->SimTime().Double();

  // Create transport node
  this->node_.reset(new gz::transport::Node());
  this->node_->Init();

  // Subscribe to robot battery state updater
  this->batterySetSub_ = this->node_->Subscribe(
      "~/battery_level/request",
      &RobotController::UpdateBattery,
      this);
  this->batterySetPub_ = this->node_->Advertise< gz::msgs::Response >(
      "~/battery_level/response");

  if (not _sdf->HasElement("rv:robot_config"))
  {
    std::cerr
        << "No `rv:robot_config` element found, controller not initialized."
        << std::endl;
    return;
  }

  auto robotConfiguration = _sdf->GetElement("rv:robot_config");

  if (robotConfiguration->HasElement("rv:update_rate"))
  {
    auto updateRate = robotConfiguration->GetElement("rv:update_rate")->Get< double >();
    this->actuationTime_ = 1.0 / updateRate;
  }

  // Load motors
  this->motorFactory_ = this->MotorFactory(_parent);
  this->LoadActuators(robotConfiguration);

  // Load sensors
  this->sensorFactory_ = this->SensorFactory(_parent);
  this->LoadSensors(robotConfiguration);

  // Load brain, this needs to be done after the motors and sensors so they
  // can potentially be reordered.
  this->LoadBrain(robotConfiguration);

  // Call the battery loader
  this->LoadBattery(robotConfiguration);

  // Call startup function which decides on actuation
  this->Startup(_parent, _sdf);
}

/////////////////////////////////////////////////
void RobotController::UpdateBattery(ConstRequestPtr &_request)
{
  if (_request->data() not_eq this->model_->GetName() and
      _request->data() not_eq this->model_->GetScopedName())
  {
    return;
  }

  gz::msgs::Response resp;
  resp.set_id(_request->id());
  resp.set_request(_request->request());

  if (_request->request() == "set_battery_level")
  {
    resp.set_response("success");
    this->SetBatteryLevel(_request->dbl_data());
  }
  else
  {
    std::stringstream ss;
    ss << this->BatteryLevel();
    resp.set_response(ss.str());
  }

  batterySetPub_->Publish(resp);
}

/////////////////////////////////////////////////
void RobotController::LoadActuators(const sdf::ElementPtr _sdf)
{
  if (not _sdf->HasElement("rv:brain")
      or not _sdf->GetElement("rv:brain")->HasElement("rv:actuators"))
  {
    return;
  }
  auto actuators = _sdf->GetElement("rv:brain")->GetElement("rv:actuators");

  // Load actuators of type servomotor
  if (actuators->HasElement("rv:servomotor"))
  {
    auto servomotor = actuators->GetElement("rv:servomotor");
    while (servomotor)
    {
      auto servomotorObj = this->motorFactory_->Create(servomotor);
      motors_.push_back(servomotorObj);
      servomotor = servomotor->GetNextElement("rv:servomotor");
    }
  }
}

/////////////////////////////////////////////////
void RobotController::LoadSensors(const sdf::ElementPtr _sdf)
{
  if (not _sdf->HasElement("rv:brain")
      or not _sdf->GetElement("rv:brain")->HasElement("rv:sensors"))
  {
    return;
  }
  auto sensors = _sdf->GetElement("rv:brain")->GetElement("rv:sensors");

  // Load sensors
  auto sensor = sensors->GetElement("rv:sensor");
  while (sensor)
  {
    auto sensorObj = this->sensorFactory_->Create(sensor);
    sensors_.push_back(sensorObj);
    sensor = sensor->GetNextElement("rv:sensor");
  }
}

/////////////////////////////////////////////////
MotorFactoryPtr RobotController::MotorFactory(
    ::gazebo::physics::ModelPtr _model)
{
  return MotorFactoryPtr(new class MotorFactory(_model));
}

/////////////////////////////////////////////////
SensorFactoryPtr RobotController::SensorFactory(
    ::gazebo::physics::ModelPtr _model)
{
  return SensorFactoryPtr(new class SensorFactory(_model));
}

/////////////////////////////////////////////////
void RobotController::LoadBrain(const sdf::ElementPtr _sdf)
{
  if (not _sdf->HasElement("rv:brain"))
  {
    std::cerr << "No robot brain detected, this is probably an error."
              << std::endl;
    return;
  }

  auto brain = _sdf->GetElement("rv:brain");
  auto controller_sdf = brain->GetElement("rv:controller");
  auto controller_type = controller_sdf->GetAttribute("type")->GetAsString();
  auto learner = brain->GetElement("rv:learner")->GetAttribute("type")->GetAsString();
  std::cout << "Loading controller " << controller_type << " and learner " << learner << std::endl;

  if ("offline" == learner and "ann" == controller_type)
  {
    brain_.reset(new NeuralNetwork(this->model_, brain, motors_, sensors_));
  }
  else if ("rlpower" == learner and "spline" == controller_type)
  {
    if (not motors_.empty()) {
        brain_.reset(new RLPower(this->model_, brain, motors_, sensors_));
    }
  }
  else if ("bo" == learner and "cpg" == controller_type)
  {
    brain_.reset(new DifferentialCPG(this->model_, _sdf, motors_, sensors_));
  }
  else if ("offline" == learner and "cpg" == controller_type)
  {
      revolve::DifferentialCPG::ControllerParams params = LoadParamsFromSDF(controller_sdf);
      brain_.reset(new DifferentialCPGClean(params, motors_));
  }
  else
  {
    throw std::runtime_error("Robot brain is not defined.");
  }
}

revolve::DifferentialCPG::ControllerParams LoadParamsFromSDF(sdf::ElementPtr controller_sdf)
{
    // TODO: make sure that it does not crash when attributes are 'None'
    revolve::DifferentialCPG::ControllerParams params;
    params.reset_neuron_random = (controller_sdf->GetAttribute("reset_neuron_random")->GetAsString() == "true");
    params.use_frame_of_reference = (controller_sdf->GetAttribute("use_frame_of_reference")->GetAsString() == "true");
    params.init_neuron_state = stod(controller_sdf->GetAttribute("init_neuron_state")->GetAsString());
    params.range_ub = stod(controller_sdf->GetAttribute("range_ub")->GetAsString());
    params.signal_factor_all = stod(controller_sdf->GetAttribute("signal_factor_all")->GetAsString());
    params.signal_factor_mid = stod(controller_sdf->GetAttribute("signal_factor_mid")->GetAsString());
    params.signal_factor_left_right = stod(controller_sdf->GetAttribute("signal_factor_left_right")->GetAsString());
    params.abs_output_bound = stod(controller_sdf->GetAttribute("abs_output_bound")->GetAsString());

    // Get the weights from the sdf:
    std::string sdf_weights = controller_sdf->GetAttribute("weights")->GetAsString();
    std::string delimiter = ";";

    size_t pos = 0;
    std::string token;
    while ((pos = sdf_weights.find(delimiter)) != std::string::npos) {
        token = sdf_weights.substr(0, pos);
        params.weights.push_back(stod(token));
        sdf_weights.erase(0, pos + delimiter.length());
    }

    return params;
}

/////////////////////////////////////////////////
/// Default startup, bind to CheckUpdate
void RobotController::Startup(
    ::gazebo::physics::ModelPtr /*_parent*/,
    sdf::ElementPtr /*_sdf*/)
{
  this->updateConnection_ = gz::event::Events::ConnectWorldUpdateBegin(
      boost::bind(&RobotController::CheckUpdate, this, _1));
}

/////////////////////////////////////////////////
void RobotController::CheckUpdate(const ::gazebo::common::UpdateInfo _info)
{
  auto diff = _info.simTime - lastActuationTime_;

  if (diff.Double() > actuationTime_)
  {
    this->DoUpdate(_info);
    lastActuationTime_ = _info.simTime;
  }
}

/////////////////////////////////////////////////
/// Default update function simply tells the brain to perform an update
void RobotController::DoUpdate(const ::gazebo::common::UpdateInfo _info)
{
  auto currentTime = _info.simTime.Double() - initTime_;

  if (brain_)
    brain_->Update(motors_, sensors_, currentTime, actuationTime_);
}

/////////////////////////////////////////////////
void RobotController::LoadBattery(const sdf::ElementPtr _sdf)
{
  if (_sdf->HasElement("rv:battery"))
  {
    this->batteryElem_ = _sdf->GetElement("rv:battery");
  }
}

/////////////////////////////////////////////////
double RobotController::BatteryLevel()
{
  if (not batteryElem_ or not batteryElem_->HasElement("rv:level"))
  {
    return 0.0;
  }

  return batteryElem_->GetElement("rv:level")->Get< double >();
}

/////////////////////////////////////////////////
void RobotController::SetBatteryLevel(double _level)
{
  if (batteryElem_ and batteryElem_->HasElement("rv:level"))
  {
    batteryElem_->GetElement("rv:level")->Set(_level);
  }
}
