// Detection throughput monitor: a lightweight C++ consumer of the
// high-frequency /detections stream. Counts messages and reports rate/sec.
#include <chrono>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class Monitor : public rclcpp::Node
{
public:
  Monitor() : Node("monitor"), count_(0)
  {
    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "detections", 10,
      [this](const std_msgs::msg::String::SharedPtr) { count_++; });

    timer_ = this->create_wall_timer(
      1s, [this]() {
        RCLCPP_INFO(this->get_logger(), "Throughput: %u detections/sec", count_);
        count_ = 0;
      });

    RCLCPP_INFO(this->get_logger(), "Monitor started, watching /detections");
  }

private:
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
  rclcpp::TimerBase::SharedPtr timer_;
  unsigned int count_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Monitor>());
  rclcpp::shutdown();
  return 0;
}
