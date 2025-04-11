import time
import sys

import device_utils as utils

TIMEOUT_SECONDS = 60
CHECK_AUTHORIZATION_INTERVAL = 3


def is_authorized_device(ip_address: str) -> bool:
    """Checks whether the Cast-enabled device is authorized to receive ADB commands from host.

    Args:
        ip_address: The IP address of the Google Cast-enabled device.

    Returns:
        A boolean indicating whether the device is authorized or not.
    """
    device_status = utils.get_device_status(ip_address)
    return device_status == "device"


def is_timeout_reached(start_time: float) -> bool:
    """
    Checks whether the timeout duration has been exceeded.

    Compares the current time to the provided start time to determine if the
    elapsed time exceeds the timeout limit TIMEOUT_SECONDS.

    Args:
        start_time: The starting time in seconds.

    Returns:
        bool: True if the timeout duration has been reached, False otherwise.
    """
    return time.time() - start_time > TIMEOUT_SECONDS


def wait_for_user_authentication_on_device(ip_address: str):
    """
    Waits for the user to authenticate the connection on a Google Cast-enabled device.

    This function checks periodically whether the user has authorized the device connection.
    If the user does not authenticate within the timeout period, the function disconnects
    from the device and exits the program.

    Args:
        ip_address: The IP address of the Cast device as a string.

    Returns:
        None
    """
    print("Please authenticate connection on Cast Device")

    start_time = time.time()
    timeout_reached = is_timeout_reached(start_time)
    authorized_device = is_authorized_device(ip_address)

    while not authorized_device and not timeout_reached:
        time.sleep(CHECK_AUTHORIZATION_INTERVAL)
        authorized_device = is_authorized_device(ip_address)
        timeout_reached = is_timeout_reached(start_time)

        if timeout_reached:
            print("Timeout reached. Exiting...")
            utils.disconnect_from_device(ip_address)
            sys.exit(0)


def pair_to_device_first_time():
    """Attempts to discover and connect to a Google Cast-enabled device on the local network.

    This function locates the IP address of a Cast-enabled device a tries to establish a connection.
    If the device requires user authorization, it waits for the user to authenticate the connection
    manually (e.g. by approving the pairing on the device itself).

    Returns:
        None
    """
    ip_address = utils.find_device_ip_address()
    authorized_connection = utils.connect_to_cast_device(ip_address)

    if not authorized_connection:
        wait_for_user_authentication_on_device(ip_address)
        print(f"Connection authorized! Connected to Cast Device at {ip_address}")
    else:
        print(f"Connected to Cast Device at {ip_address}. No need to authenticate connection.")


if __name__ == '__main__':
    pair_to_device_first_time()