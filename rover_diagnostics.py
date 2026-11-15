# Import the os library to access environment variables
import os

# Import Yuridia's ROS 2 diagnostic functions
from ros2_checks import run_ros2_checks

# Import the networking and hardware diagnostic functions
from network_checks import run_network_checks


# -------------------------------------------------
# Main Diagnostic Program
# -------------------------------------------------
def main():

    # Display the program title
    print("=" * 45)
    print("       TASC ROVER DIAGNOSTICS")
    print("=" * 45)

    # -------------------------------------------------
    # Part 1: ROS 2 Diagnostics
    # -------------------------------------------------

    print("\n===== ROS 2 DIAGNOSTICS =====")

    # Run all ROS 2 checks and store their counters
    ros_results = run_ros2_checks()

    # -------------------------------------------------
    # Part 2: Network and Hardware Diagnostics
    # -------------------------------------------------

    # Get the base station IP address from the environment
    base_ip = os.environ.get("TASC_BASE_IP")

    # Run networking and hardware checks
    network_results = run_network_checks(base_ip)

    # -------------------------------------------------
    # Count Network and Hardware Results
    # -------------------------------------------------

    # Count successful network and hardware checks
    network_pass = sum(
        result["status"] == "PASS"
        for result in network_results
    )

    # Count warning results
    network_warn = sum(
        result["status"] == "WARN"
        for result in network_results
    )

    # Count failed results
    network_fail = sum(
        result["status"] == "FAIL"
        for result in network_results
    )

    # -------------------------------------------------
    # Combine Results From Both Modules
    # -------------------------------------------------

    # Add the ROS 2 and networking PASS counters
    total_pass = ros_results["PASS"] + network_pass

    # Add the ROS 2 and networking WARN counters
    total_warn = ros_results["WARN"] + network_warn

    # Add the ROS 2 and networking FAIL counters
    total_fail = ros_results["FAIL"] + network_fail

    # -------------------------------------------------
    # Display Overall Diagnostic Summary
    # -------------------------------------------------

    print("\n====================================")
    print("       OVERALL DIAGNOSTIC SUMMARY")
    print("====================================")

    # Display the total number of each result
    print(f"PASS: {total_pass}")
    print(f"WARN: {total_warn}")
    print(f"FAIL: {total_fail}")

    # Display a final message based on the results
    if total_fail > 0:
        print("\n[FAIL] Some diagnostic checks failed.")

    elif total_warn > 0:
        print("\n[WARN] Diagnostics completed with warnings.")

    else:
        print("\n[PASS] All diagnostic checks passed.")


# -------------------------------------------------
# Start the Program
# -------------------------------------------------
if __name__ == "__main__":

    # Call the main function when this file is executed
    main()
