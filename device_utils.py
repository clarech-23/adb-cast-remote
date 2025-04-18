import sys
import subprocess
from typing import Optional


def find_device_ip_address() -> str:
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


def connect_to_cast_device(ip_address: str, quiet_connect: bool = False) -> Optional[bool]:
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
        A boolean indicating if the host has successfully connected to the device and the
        device has authorized receiving ADB commands from the host. If connecting quietly,
        return None.

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
        device_status = get_device_status(ip_address)

    if connection_outcome == f"connected to {ip_address}:5555":
        print(f"Connected to device {ip_address}")
        return True

    if "already connected" in connection_outcome and device_status == "device":
        print(f"Already connected to {ip_address}:5555")
        return True

    if "already connected" in connection_outcome and device_status != "device":
        print(f"Connection to device {ip_address} is unauthorized")
        return False

    if "failed to authenticate" in connection_outcome:
        print(f"Failed to authenticate connection to device {ip_address}")
        return False

    if connection_outcome == f"failed to connect to '{ip_address}:5555': Connection refused":
        raise RuntimeError(f"Unable to connect to device at {ip_address}. Check if Developer Options and USB Debugging"
                           f"is enabled on device.")

    if connection_outcome == f"failed to connect to '{ip_address}:5555': No route to host":
        raise RuntimeError(f"Unable to connect to device at {ip_address}. Check if device is connected to the local "
                           f"network")

    if connection_outcome == f"failed to resolve host '{ip_address}': Name or service not known":
        raise RuntimeError(f"{ip_address} is an invalid IP address")

    raise RuntimeError(f"Unexpected connection outcome: {connection_outcome}")


def disconnect_from_device(ip_address: str):
    """Disconnects from a Google Cast-enabled device on the local network.

    Args:
        ip_address: The IP address of the Google Cast-enabled device.
    """
    output = subprocess.run(f'adb disconnect {ip_address}', shell=True,
                            capture_output=True, text=True)
    print(repr(output.stdout))
    if "disconnect" in output.stdout:
        print(f"Disconnected from device {ip_address}")
    else:
        raise RuntimeError(f"No such device {ip_address}")


def get_device_status(ip_address: str) -> str:
    """Fetches the Android Debug Bridge connection status for the Google Cast-enabled device.

    If the device is found, the status can be one of the following:
        'device': Device is connected and authorized
        'unauthorized': Device is connected but unauthorized
        'offline': Host unable to communicate with Cast-enabled device
    
    Args:
        ip_address: The IPv4 address of the Google Cast-enabled device.

    Returns:
        The connection status of the device as a string, if found. Returns empty string if
        the device was not found.

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