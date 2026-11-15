# Import libraries used for network and hardware diagnostics
import subprocess
import json
import os
import glob


# -------------------------------------------------
# Run a Linux Terminal Command
# -------------------------------------------------
def run_command(command, timeout=5):

    try:
        # Execute the command and capture its output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Return the command result
        return result

    except FileNotFoundError:
        # The command does not exist on the system
        return None

    except subprocess.TimeoutExpired:
        # The command took too long to complete
        return None


# -------------------------------------------------
# Check 1: Network Interfaces and IP Addresses
# -------------------------------------------------
def check_network_interfaces():

    print("\n===== NETWORK INTERFACE CHECK =====")

    # Run the Ubuntu command to get network information
    # -j makes the command return JSON data
    result = run_command(["ip", "-j", "addr", "show"])

    # Check whether the command executed successfully
    if result is None or result.returncode != 0:

        print("[FAIL] Unable to check network interfaces")

        return {
            "status": "FAIL",
            "message": "Unable to check network interfaces"
        }

    try:
        # Convert the JSON output into Python data
        interfaces = json.loads(result.stdout)

    except json.JSONDecodeError:

        print("[FAIL] Invalid network information")

        return {
            "status": "FAIL",
            "message": "Invalid network information"
        }

    # Store the names of active network interfaces
    active_interfaces = []

    # Examine each network interface
    for interface in interfaces:

        # Get the interface name
        name = interface.get("ifname", "Unknown")

        # Ignore the loopback interface
        # It is used for communication within the computer
        if name == "lo":
            continue

        # Get the interface's operating state
        state = interface.get("operstate", "UNKNOWN")

        # Get interface flags such as UP and LOWER_UP
        flags = interface.get("flags", [])

        # Extract IPv4 addresses assigned to the interface
        addresses = [
            address.get("local")
            for address in interface.get("addr_info", [])
            if address.get("family") == "inet"
            and address.get("local")
        ]

        # Display information about the interface
        print(f"\nInterface: {name}")
        print(f"State: {state}")

        print(
            f"IPv4 Address: "
            f"{', '.join(addresses) if addresses else 'None'}"
        )

        # LOWER_UP means the interface reports an active link
        # An IPv4 address is also required for this PASS condition
        if "LOWER_UP" in flags and addresses:

            print("[PASS] Interface is active")

            # Add the interface to the active list
            active_interfaces.append(name)

        else:
            print("[WARN] Interface inactive or missing IPv4")

    # Check whether at least one active interface was found
    if active_interfaces:

        message = "Active interfaces: " + ", ".join(active_interfaces)

        print(f"\n[PASS] {message}")

        return {
            "status": "PASS",
            "message": message
        }

    else:

        print("\n[FAIL] No active IPv4 interfaces found")

        return {
            "status": "FAIL",
            "message": "No active IPv4 interfaces found"
        }


# -------------------------------------------------
# Check 2: Base Station Connectivity
# -------------------------------------------------
def check_base_station(base_ip):

    print("\n===== BASE STATION CONNECTIVITY =====")

    # Check whether the base station IP address was provided
    if not base_ip:

        print("[WARN] Base station IP address not configured")

        return {
            "status": "WARN",
            "message": "Base station IP address not configured"
        }

    # Send three ping requests to the base station
    # -c 3 sends three packets
    # -W 2 waits up to two seconds for each response
    result = run_command(
        ["ping", "-c", "3", "-W", "2", base_ip],
        timeout=10
    )

    # Check whether ping was unavailable or timed out
    if result is None:

        print("[FAIL] Ping command unavailable or timed out")

        return {
            "status": "FAIL",
            "message": "Ping command unavailable or timed out"
        }

    # A return code of 0 means ping was successful
    if result.returncode == 0:

        print(f"[PASS] Base station {base_ip} is reachable")

        return {
            "status": "PASS",
            "message": f"Base station {base_ip} is reachable"
        }

    else:

        # Ping failed to receive a successful response
        print(f"[FAIL] Cannot reach base station {base_ip}")

        print("       Check Wi-Fi, Ethernet, or IP configuration")

        return {
            "status": "FAIL",
            "message": f"Cannot reach base station {base_ip}"
        }

# -------------------------------------------------
# Check 3: ESP32 Serial Devices
# -------------------------------------------------
def check_esp32():

    print("\n===== ESP32 SERIAL DEVICE CHECK =====")

    # Search for common Linux USB serial device names
    devices = sorted(set(
        glob.glob("/dev/ttyUSB*") +
        glob.glob("/dev/ttyACM*")
    ))

    # Check whether any serial devices were found
    if not devices:

        print("[WARN] No USB serial devices detected")

        return {
            "status": "WARN",
            "message": "No USB serial devices detected"
        }

    # Display the serial devices found
    print("Possible ESP32 serial devices:")

    for device in devices:
        print(f"  {device}")

    # These ports could belong to an ESP32 or another device
    # Additional identification is required
    print("[WARN] Serial devices found, but ESP32 identity is unverified")

    return {
        "status": "WARN",
        "message": "Possible ESP32 serial devices: " + ", ".join(devices)
    }


# -------------------------------------------------
# Check 4: Phidget Controllers
# -------------------------------------------------
def check_phidget():

    print("\n===== PHIDGET CONTROLLER CHECK =====")

    try:
        # Import the Phidget22 device manager
        from Phidget22.Devices.Manager import Manager

    except ImportError:

        # The Phidget22 Python library is not available
        print("[WARN] Phidget22 Python library not installed")

        return {
            "status": "WARN",
            "message": "Phidget22 Python library not installed"
        }

    # Store the manager so it can be closed later
    manager = None

    try:
        # Create and open the Phidget device manager
        manager = Manager()
        manager.open()

        # Give the manager time to discover connected devices
        import time
        time.sleep(2)

        # Get the list of attached Phidget devices
        devices = manager.getAttachedDevices()

        # Check whether any Phidget devices were detected
        if devices:

            print(f"[PASS] {len(devices)} Phidget device(s) detected")

            return {
                "status": "PASS",
                "message": f"{len(devices)} Phidget device(s) detected"
            }

        else:

            print("[WARN] No Phidget devices detected")

            return {
                "status": "WARN",
                "message": "No Phidget devices detected"
            }

    except Exception as error:

        # Report any error encountered during detection
        print(f"[WARN] Phidget check unavailable: {error}")

        return {
            "status": "WARN",
            "message": f"Phidget check unavailable: {error}"
        }

    finally:

        # Close the manager after checking the devices
        if manager is not None:

            try:
                manager.close()

            except Exception:
                pass


# -------------------------------------------------
# Run All Network and Hardware Checks
# -------------------------------------------------
def run_network_checks(base_ip=None):

    # Display the diagnostics heading
    print("\n====================================")
    print("       TASC ROVER DIAGNOSTICS")
    print("       NETWORK AND HARDWARE")
    print("====================================")

    # Store the results of each diagnostic check
    results = []

    # Check network interfaces and IP addresses
    results.append(check_network_interfaces())

    # Check connectivity with the base station
    results.append(check_base_station(base_ip))

    # Check for possible ESP32 serial devices
    results.append(check_esp32())

    # Check for connected Phidget devices
    results.append(check_phidget())

    # Display the final summary
    print("\n====================================")
    print("          FINAL SUMMARY")
    print("====================================")

    # Print the status and message of every check
    for result in results:
        print(f"[{result['status']}] {result['message']}")

    # Count the number of PASS, WARN, and FAIL results
    passed = sum(r["status"] == "PASS" for r in results)
    warned = sum(r["status"] == "WARN" for r in results)
    failed = sum(r["status"] == "FAIL" for r in results)

    # Display the totals
    print("\nResults:")
    print(f"PASS: {passed}")
    print(f"WARN: {warned}")
    print(f"FAIL: {failed}")

    # Return the results for use by the main program
    return results


# -------------------------------------------------
# Run This File Directly
# -------------------------------------------------
if __name__ == "__main__":

    # Read the base station IP from an environment variable
    base_station_ip = os.environ.get("TASC_BASE_IP")

    # Start the network and hardware diagnostics
    run_network_checks(base_station_ip)
