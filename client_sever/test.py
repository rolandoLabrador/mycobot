from pymycobot.mycobot280 import MyCobot280
import time
#Enter the above code to import the required packages for the project

# MyCobot280 class initialization requires two parameters:
    # The first is the serial port string, such as:
        # linux: "/dev/ttyUSB0"
        # windows: "COM3"
        # The second is the baud rate:
        # M5 version: 115200

    # For example:
        # mycobot-M5:
            # linux:
            # mc = MyCobot280("/dev/ttyUSB0", 1000000)
            # windows:
            # mc = MyCobot280("COM3", 115200)

# Initialize a MyCobo280 object
# The following is the object creation code for the windows version
mc = MyCobot280("COM3", 115200)

def pump_on():
    try:
        # Set pin 5 (G5) to LOW to turn on the suction pump
        mc.set_basic_output(2, 0)
        time.sleep(0.05)  # Wait for the pump to turn on
        print("Suction pump turned on.")
    except Exception as e:
        # Catch potential errors during __init_s
        print(f"\nAn error occurred: {e}")

# Stop suction pump
def pump_off():
    try:
        # Set pin 5 (G5) to HIGH to turn off the suction pump
        mc.set_basic_output(2, 1)
        time.sleep(0.05)  # Wait for the pump to start turning off
        # Set pin 2 (G2) to LOW and then HIGH to ensure the pump is fully off
        mc.set_basic_output(5, 0)
        time.sleep(1)  # Wait for the pump to fully turn off
        mc.set_basic_output(5, 1)
        time.sleep(0.05)  # Wait for the pump to be fully off
        print("Suction pump turned off.")
    except Exception as e:
            # Catch potential errors during __init__ or outside command calls
            print(f"\nAn error occurred: {e}")
for count in range(5):
    # Set a loop
    mc.set_basic_output(5,0)
    # Put basic2 into working state
    mc.set_basic_output(2,0)
    # Put basic position 5 into working state
    time.sleep(2)
    # Wait for two seconds
    mc.set_basic_output(5,1)
    # Stop basic position 2 from working
    mc.set_basic_output(2,1)
    # Stop basic position 2 from working

while True:
    try:
        # Set a loop
        pump_on()        # Put basic position 5 into working state
        time.sleep(10)
        # Wait for two seconds
        pump_off()       # Stop basic position 2 from working
        # Stop basic position 2 from working
        time.sleep(10)
    #keyintercept the exception
    except KeyboardInterrupt:
        # If the program is interrupted, the loop will be exited
        break