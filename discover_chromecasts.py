import pychromecast
import asyncio
from bleak import BleakScanner

async def find_chromecast_bluetooth():
    devices = await BleakScanner.discover(timeout=20)
    for d in devices:
        print(d)

def find_chromecast():
    chromecasts, browser = pychromecast.get_chromecasts()
    browser.stop_discovery()

    for cast in chromecasts:
        print("Friendly name:", cast.cast_info.friendly_name)
        print("IP address: ", cast.cast_info.host)  # This will be used to connect to the Chromecast
        print("UUID: ", cast.cast_info.uuid)  # This will be cached

    return


if __name__ == "__main__":
    find_chromecast()
    #asyncio.run(find_chromecast_bluetooth())

# Connecting for the first time:
# - Press a button to connect for first time
# - Raspberry Pi runs this script
# - Finds the IP address of the Chromecast connected to the local network (how?)
# - - Run adb kill/start-server? (I think this is only needed for the auto-connect)
# - - Run adb connect ____
# - Will also need to cache the hostname
# - User will need to authenticate using the Google Controller and press "always remember"
#
# TESTS:
# - Pi isn't connected at first -> Run script -> Pi is connected now (how to check?)
# - - adb devices
# - - mock??
# - Case #1: No Chromecast found on the local network -> do nothing
# - Case #2: There is a Chromecast found on the local network but user does not authenticate within a given amount of time
# - Case #3: There is a Chromecast found on the local network and the user authenticates in time
