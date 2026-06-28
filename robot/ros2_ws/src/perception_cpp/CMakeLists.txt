cmake_minimum_required(VERSION 3.8)
project(perception_cpp)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(monitor src/monitor.cpp)
ament_target_dependencies(monitor rclcpp std_msgs)

install(TARGETS monitor
  DESTINATION lib/${PROJECT_NAME})

ament_package()
