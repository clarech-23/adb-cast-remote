#!/usr/bin/python3

# Note: We are assuming only one Chromecast on the local network right
#       now, meaning no need for hostnames mapping to IP addresses

import device_utils as utils

if __name__ == "__main__":
    utils.restart_adb_server()
    ip_address = utils.get_ip_address()
    utils.attempt_to_connect(ip_address)