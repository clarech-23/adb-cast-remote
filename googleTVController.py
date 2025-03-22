import RPi.GPIO as GPIO
import subprocess
import signal
import sys

gpio_to_keycode = {
    27: "KEYCODE_DPAD_CENTER",  # Select
    17: "KEYCODE_DPAD_UP",
    22: "KEYCODE_DPAD_DOWN",
    23: "KEYCODE_DPAD_LEFT",
    24: "KEYCODE_DPAD_RIGHT",
    25: "KEYCODE_BACK",
    5: "KEYCODE_HOME",
    6: "KEYCODE_VOLUME_UP",
    16: "KEYCODE_VOLUME_DOWN",
    26: "KEYCODE_POWER",
}


# Function to send ABD command
def send_adb_command(gpio):
    keycode = gpio_to_keycode[gpio]
    print(f"Sending command {keycode}")
    command = f"adb shell input keyevent {keycode}"
    subprocess.run(command.split())


def exit_handler():
    print("\nExiting... Cleaning up GPIO.")
    GPIO.cleanup()
    sys.exit(0)  # Is this necessary?


# Set GPIO pins to Broadcast Mode
GPIO.setmode(GPIO.BCM)

# Configure each GPIO pins
for gpio in gpio_to_keycode:
    GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Pull-down resistor

# Detect button press (LOW -> HIGH)
for gpio in gpio_to_keycode:
    GPIO.add_event_detect(gpio, GPIO.RISING, callback=send_adb_command,
                          bouncetime=200)

# Catch Ctrl+C (SIGINT) and Stop (SIGTERM)
signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)  # This doesn't work in Thonny

try:
    print("Waiting for button press...")
    signal.pause()  # Script idles (and has 0 CPU usage) until button is pressed

finally:
    print("Exiting... Cleaning up GPIO")
    GPIO.cleanup()

