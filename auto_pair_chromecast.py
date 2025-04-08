#!/usr/bin/python3

# Note: We are assuming only one Chromecast on the local network right
#       now, meaning no need for hostnames mapping to IP addresses

import device_utils as utils

def attempt_auto_pair(address: str):
    """Attempts to connect to a Cast-enabled device at the given IP address.

    The connection should succeed only if the Cast-enabled device has previously
    remembered the host. That is, the user had selected the "Always Allow" option
    the last time the host attempted to authorize its connection to the device.

    Args:
        address: The IPv4 address of the Google Cast-enabled device.
    """
    utils.connect_to_device(address, quiet_connect=True)

    connection_status = utils.get_device_status(address)
    print(f"Connection status: {connection_status}\n")

    if connection_status == "device":
        print("Remote control connected!")
    elif connection_status == "unauthorized":
        print("Connection unauthorized. Forgetting Chromecast...")
    elif connection_status == "offline":
        print("Chromecast is offline")
    else:
        raise NotImplementedError(f"Handling of unknown connection status: {connection_status} not yet implemented")

if __name__ == "__main__":
    utils.restart_adb_server()
    ip_address = utils.get_ip_address()
    attempt_auto_pair(ip_address)