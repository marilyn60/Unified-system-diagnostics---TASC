# Import libraries needed for ROS 2 diagnostics
import shutil
import os
import subprocess


# Counters to keep track of the diagnostic results
PASS = 0
WARN = 0
FAIL = 0


# Print the result of each diagnostic check
def print_result(status, name, detail=""):
    global PASS, WARN, FAIL

    # Display the status, check name, and additional information
    print(f"[{status:<4}] {name:<32} {detail}")

    # Update the corresponding counter
    if status == "PASS":
        PASS += 1
    elif status == "WARN":
        WARN += 1
    else:
        FAIL += 1


# -------------------------------------------------
# Check 1: ROS 2 Installation
# -------------------------------------------------
def installation_check():

    # Look for the ros2 command in the system
    command = "ros2"
    cmd_path = shutil.which(command)

    # If the command exists, ROS 2 is accessible
    if cmd_path:
        print_result("PASS", "ROS 2 installed", cmd_path)
    else:
        print_result(
            "FAIL",
            "ROS 2 installed",
            "Not found - source setup.bash or install ROS 2"
        )


# -------------------------------------------------
# Check 2: ROS 2 Distribution
# -------------------------------------------------
def distribution_check():

    # Read the ROS_DISTRO environment variable
    distro = os.environ.get("ROS_DISTRO")

    # Check whether the configured distribution is Jazzy
    if distro == "jazzy":
        print_result("PASS", "ROS_DISTRO", distro)

    elif distro:
        print_result(
            "WARN",
            "ROS_DISTRO",
            f"Expected jazzy, found {distro}"
        )

    else:
        print_result(
            "FAIL",
            "ROS_DISTRO",
            "Not set - source setup.bash"
        )


# -------------------------------------------------
# Check 3: ROS Domain ID
# -------------------------------------------------
def domain_check():

    # Read the ROS_DOMAIN_ID environment variable
    domain = os.environ.get("ROS_DOMAIN_ID")

    # Display the configured domain ID
    if domain:
        print_result("PASS", "ROS_DOMAIN_ID", domain)

    else:
        # ROS 2 normally uses domain 0 if none is specified
        print_result(
            "WARN",
            "ROS_DOMAIN_ID",
            "Not set (defaults to 0)"
        )


# -------------------------------------------------
# Check 4: ROS 2 Environment Configuration
# -------------------------------------------------
def env_config_check():

    # Read environment variables used by ROS 2
    ros_version = os.environ.get("ROS_VERSION")
    ament = os.environ.get("AMENT_PREFIX_PATH")

    # ROS_VERSION should be 2, and AMENT_PREFIX_PATH
    # should be configured
    if ros_version == "2" and ament:
        print_result("PASS", "ENVIRONMENT")

    else:
        print_result(
            "FAIL",
            "ENVIRONMENT",
            "Not sourced - source setup.bash"
        )


# -------------------------------------------------
# Check 5: Active ROS 2 Nodes
# -------------------------------------------------
def active_nodes_check():

    # Command used to list available ROS 2 nodes
    command = "ros2 node list"

    # Execute the command and collect its output
    cmd_path = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    # Check whether the command executed successfully
    if cmd_path.returncode != 0:
        print_result(
            "FAIL",
            "ACTIVE_NODE",
            "Command did not run successfully"
        )

    # If there is no output, no nodes were discovered
    elif cmd_path.stdout.strip() == "":
        print_result(
            "WARN",
            "ACTIVE_NODE",
            "No active nodes found"
        )

    else:
        # Count the nodes listed in the output
        count = len(cmd_path.stdout.strip().splitlines())

        print_result(
            "PASS",
            "ACTIVE_NODE",
            f"{count} discovered"
        )


# -------------------------------------------------
# Check 6: Active ROS 2 Topics
# -------------------------------------------------
def active_topics_check():

    # Command used to list available ROS 2 topics
    command = "ros2 topic list"

    # Execute the command
    cmd_path = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    # Check whether the command executed successfully
    if cmd_path.returncode != 0:
        print_result(
            "FAIL",
            "ACTIVE_TOPICS",
            "Command did not run successfully"
        )

    # Check whether any topics were discovered
    elif cmd_path.stdout.strip() == "":
        print_result(
            "WARN",
            "ACTIVE_TOPICS",
            "No active topics found"
        )

    else:
        # Count the available topics
        count = len(cmd_path.stdout.strip().splitlines())

        print_result(
            "PASS",
            "ACTIVE_TOPICS",
            f"{count} discovered"
        )


# -------------------------------------------------
# Check 7: ROS 2 Controller Manager
# -------------------------------------------------
def controller_check():

    # Command used to list ROS 2 controllers
    command = "ros2 control list_controllers"

    # Execute the controller command
    cmd_path = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    # A failed command may indicate a missing controller
    # manager, missing package, or configuration problem
    if cmd_path.returncode != 0:
        print_result(
            "WARN",
            "CONTROLLER_CHECK",
            "Controller check unavailable"
        )

    # Check whether the command returned controller information
    elif cmd_path.stdout.strip() == "":
        print_result(
            "WARN",
            "CONTROLLER_CHECK",
            "No controllers listed"
        )

    else:
        # Count the lines containing controller information
        count = len(cmd_path.stdout.strip().splitlines())

        print_result(
            "PASS",
            "CONTROLLER_CHECK",
            f"{count} output line(s) returned"
        )


# -------------------------------------------------
# Run All ROS 2 Checks
# -------------------------------------------------
def run_ros2_checks():
    global PASS, WARN, FAIL

    # Reset counters before starting the diagnostics
    PASS = WARN = FAIL = 0

    # Run each ROS 2 diagnostic function
    installation_check()
    distribution_check()
    domain_check()
    env_config_check()
    active_nodes_check()
    active_topics_check()
    controller_check()

    # Return the results to the main program
    return {
        "PASS": PASS,
        "WARN": WARN,
        "FAIL": FAIL
    }


# Run the ROS 2 checks if this file is executed directly
if __name__ == "__main__":
    results = run_ros2_checks()
    print("\nROS 2 Results:", results)
