import subprocess


def get_ip_address() -> str:
    """Fetches the IP address of a Google Cast-enabled device connected to the local network.

    Assumptions:
        Only one Google Cast-enabled device can be connected to the local network.

    Returns:
        A string containing the IP address of the Google Cast-enabled device.

    Raises:
        # TODO: What happens if there are more than one Cast-enabled device?
    """
    cmd = "avahi-browse -rt _googlecast._tcp | \
	       grep -E 'IPv4|address' | awk '{print $3}' | grep '\.' | \
	       tr -d '[]'"
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    ip_address = output.stdout.strip()

    if ip_address == "":
        print("No Google Cast-enabled device found on local network.")
        # TODO: What should be returned if no IP address was found?
    else:
        print(f"Google Cast-enabled device on local network: {ip_address}")

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


# def connect_to_device(address: str, quiet_connect: bool) -> str:
def connect_with_authorization_prompt(ip_address: str) -> str:
    """Connects to the Cast-enabled device, triggering an authorization prompt if required.
    # TODO: I THINK THIS IS MORE SUITED FOR ATTEMPT_TO_CONNECT
    Developer Options and ADB Debugging must be enabled on the Google Cast-enabled device to
    allow connection. An authorization prompt will appear on the device screen if it does not
    recognize the host.

    Args:
        ip_address: The IPv4 address of the Google Cast-enabled device.

    Returns:
        A string of the output of the ADB connection command.
    """
    cmd = f"adb connect {ip_address}:5555"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    return result.stdout.strip()


def connect_quietly(address: str) -> str:
    """
    Connect to the Chromecast using Android Debug Bridge without
    triggering the authorization popup to appear on the Chromecast GUI.

    Parameters:
    -----------
    address: str
        The IP address of the device

    Returns:
    --------
    str
        A statement regarding the outcome of the connection

    """
    cmd = f"adb -a connect {address}:5555"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # TODO: What happens if there is an error?

    return result.stdout.strip()


def get_connection_status(ip_address: str) -> str:
    """Fetches the Android Debug Bridge connection status for the Google Cast-enabled device.

    If found, the status can be one of the following:
        'offline': Device is offline
        'unauthorized': Device is connected but unauthorized
        'device': Device is connected and authorized
    
    Args:
        ip_address: The IPv4 address of the Google Cast-enabled device.

    Returns:
        The connection status of the device, if found. Returns an empty string if the
         device is not listed.
    """
    cmd = f"adb devices | grep {ip_address} | awk '{{print $2}}'"
    result = subprocess.run(cmd, shell=True, capture_output=True,
                            text=True)

    return result.stdout.strip()


def attempt_to_connect(ip_address: str):  # TODO: add argument for quietly or not
    """Attempts to connect to a Cast-enabled device at the given IP address.

    The connection should succeed only if the Cast-enabled device has previously
    remembered the host. That is, the user had selected the "Always Allow" option
    the last time the host attempted to authorize its connection to the device.

    Args:
        ip_address: The IPv4 address of the Google Cast-enabled device.
    """
    attempt_outcome = connect_quietly(ip_address)
    print(f"Connection attempt outcome: {attempt_outcome}")

    connection_status = get_connection_status(ip_address)
    print(f"Connection status: {connection_status}\n")

    if connection_status == "device":
        print("Remote control connected!")
    elif connection_status == "":
        print("Connection refused")
    elif connection_status == "unauthorized":
        print("Connection unauthorized. Forgetting Chromecast...")
    # TODO: Delete hostname from txt
    elif connection_status == "offline":
        print("Chromecast is offline")
    else:
        print("Error: Unknown connection status")