import subprocess

# Note: We are assuming only one Chromecast on the local network right now
def find_chromecast_on_network() -> str:
    """
    Finds the IP address of the Chromecast on network

    Returns:
        str: The IP address of the Chromecast on network
    """
    cmd = "avahi-browse -rt _googlecast._tcp | grep -E 'IPv4|address' | awk '{print $3}' | grep '\.' | tr -d '[]'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    print(result)

    return "Done"



if __name__ == "__main__":
    print(find_chromecast_on_network())
