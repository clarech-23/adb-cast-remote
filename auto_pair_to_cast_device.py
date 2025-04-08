#!/usr/bin/python3

import subprocess
import device_utils as utils

def auto_pair_to_device(address: str):
    """Attempts to connect to a Cast-enabled device at the given IP address.

    The connection should succeed only if the Cast-enabled device has previously
    remembered the host. That is, the user had selected the "Always Allow" option
    the last time the host attempted to authorize its connection to the device.

    Args:
        address: The IPv4 address of the Google Cast-enabled device.
    """
    utils.connect_to_cast_device(address, quiet_connect=True)
    connection_status = utils.get_device_status(address)

    if connection_status == "device":
        print(f"Connected to Google Cast-enabled device at {address}!")
    elif connection_status == "unauthorized":
        print(f"Connection to Google Cast-enabled device at {address} is unauthorized. Forgetting device...")
        subprocess.run(f"adb disconnect {address}", shell=True)
    elif connection_status == "offline":
        print("Unable to connect to Google Cast-enabled device.")
    else:
        raise NotImplementedError(f"Handling of unknown connection status: {connection_status} not yet implemented.")

if __name__ == "__main__":
    ip_address = utils.get_ip_address()
    auto_pair_to_device(ip_address)