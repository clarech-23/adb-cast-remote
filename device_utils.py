import sys
import subprocess
from typing import Optional


def get_ip_address() -> str:
    """Fetches the IP address of a Google Cast-enabled device connected to the local network.

    Assumptions:
        Only one Google Cast-enabled device can be connected to the local network.

    Returns:
        A string containing the IP address of the Google Cast-enabled device.

    Raises:
        NotImplementedError: If multiple Google Cast-enabled devices are found (not yet supported).
    """
    cmd = (
        r"avahi-browse -rt _googlecast._tcp | "
	    r"grep -E 'IPv4|address' | awk '{print $3}' | grep '\.' | "
	    r"tr -d '[]'"
    )
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    list_ip_addresses = output.stdout.splitlines()

    if len(list_ip_addresses) == 0:
        print("No Google Cast-enabled devices found on the local network.")
        sys.exit(0)
    if len(list_ip_addresses) > 1:
        raise NotImplementedError("This function currently supports only a single Cast-enabled device."
                                  "Handling of multiple Cast-enabled devices is not yet supported.")

    ip_address = list_ip_addresses[0]
    print(f"Google Cast-enabled device IP address: {ip_address}")

    return ip_address


def restart_adb_server():
    """Restarts the Android Debug Bridge (ADB) daemon.

    This is useful for refreshing the ADB connection, especially when
    devices are not detected, or ADB is behaving unexpectedly.
    """
    cmd_kill_server = "adb kill-server"
    cmd_start_server = "adb start-server"

    subprocess.run(cmd_kill_server, shell=True)
    subprocess.run(cmd_start_server, shell=True)


def connect_to_cast_device(ip_address: str, quiet_connect: bool = False) -> Optional[str]:
    """Connects to a Google Cast-enabled device on the local network.

    Sends the Android Debug Bridge (ADB) connection command to the Cast-enabled device.
    Developer Options and ADB Debugging must be enabled on the Cast-enabled device to
    allow connection. An authorization popup will appear on the device screen if it does not
    recognize the host.

    Args:
        ip_address: The IP address of the Google Cast-enabled device.
        quiet_connect: A boolean indicating whether to suppress the authorization popup
                       on the device.

    Returns:
        The terminal output of the ADB connection command as a string, which describes
        the outcome of the connection attempt. If connecting quietly, return None.

    Raises:
        RuntimeError: If unable to connect to Cast-enabled device.
    """
    if quiet_connect:
        cmd = f"abd -a connect {ip_address}:5555"
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return None
    else:
        cmd = f"adb connect {ip_address}:5555"
        connection_outcome = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

    if connection_outcome == f"connected to {ip_address}:5555":
        print(f"Connected to device at {ip_address}")
    elif connection_outcome == f"already connected to {ip_address}:5555":
        print(f"Already connected to device at {ip_address}")
    elif connection_outcome == f"failed to authenticate to {ip_address}:5555":
        print(f"Failed to authenticate connection to device at {ip_address}")
    elif connection_outcome == f"failed to connect to '{ip_address}:5555': Connection refused":
        raise RuntimeError(f"Unable to connect to device at {ip_address}. Check if Developer Options and USB Debugging"
                           f"is enabled on device.")
    elif connection_outcome == f"failed to connect to '{ip_address}:5555': No route to host":
        raise RuntimeError(f"Unable to connect to device at {ip_address}. Check if device is connected to the local "
                           f"network")
    elif connection_outcome == f"failed to resolve host '{ip_address}': Name or service not known":
        raise RuntimeError(f"{ip_address} is an invalid IP address")
    else:
        raise RuntimeError(f"Unexpected connection outcome: {connection_outcome}")

    return connection_outcome


def get_device_status(ip_address: str) -> str:
    """Fetches the Android Debug Bridge connection status for the Google Cast-enabled device.

    If the device with the corresponding IP address is not found, an empty string is returned.
    If the device is found, the status can be one of the following:
        'offline': Host unable to communicate with Cast-enabled device
        'unauthorized': Device is connected but unauthorized
        'device': Device is connected and authorized
    
    Args:
        ip_address: The IPv4 address of the Google Cast-enabled device.

    Returns:
        The connection status of the device, if found.

    Raises:
        RuntimeError: If no device with the corresponding IP address was found.
    """
    cmd = f"adb devices | grep {ip_address} | awk '{{print $2}}'"
    output = subprocess.run(cmd, shell=True, capture_output=True,
                            text=True)

    device_status = output.stdout.strip()

    if device_status == "":
        raise RuntimeError(f"No device with IP address {ip_address} found.")

    return device_status