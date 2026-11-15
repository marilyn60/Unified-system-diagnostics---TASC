# TASC Rover Diagnostics

## About the Project

This project is a Python script that checks the ROS 2 system, network connections, and hardware on the TASC rover.

The goal is to make troubleshooting easier by running different checks using one command instead of checking everything separately.

The program displays three types of results:

- PASS: The check was successful.
- WARN: Something might need attention.
- FAIL: Something is not working correctly.

## Project Files

The project has three Python files:

- ros2_checks.py: Checks the ROS 2 installation, distribution, domain ID, environment, active nodes, topics, and controller manager.
- network_checks.py: Checks network interfaces, base station connectivity, ESP32 serial devices, and Phidget controllers.
- rover_diagnostics.py: Runs both files together and displays the overall results.

## Requirements

- Ubuntu Linux
- Python 3
- ROS 2 Jazzy
- Phidget22 Python library (for checking Phidget devices)

## How to Run

1. Open the project folder:

   cd ~/tasc-rover-diagnostics

2. Set up ROS 2:

   source /opt/ros/jazzy/setup.bash

3. Run the program:

   python3 rover_diagnostics.py

## Running Files Separately

To run only the ROS 2 checks:

python3 ros2_checks.py

To run only the network and hardware checks:

python3 network_checks.py

## Notes

- Some warnings are normal if the program is running on a virtual machine instead of the actual rover.
- If the base station IP address is not provided, the program will display a warning.
- The ESP32 check looks for USB serial devices but cannot confirm whether they are ESP32 devices.
- The Phidget check requires the Phidget22 Python library.
- The program should also be tested on the actual rover to confirm that the hardware checks work correctly.

## Team Members

TASC Communications & Controls

- Yuridia: ROS 2 checks
- Nabiha: Network and hardware checks
- Both parts were combined into one diagnostics program.
