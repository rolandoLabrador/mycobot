#from webBotSocket import MyCobotWebots
from pymycobot import MyCobot280
import cv2
import numpy as np
import asyncio
import json
import time
from pump_controller import SerialControl
import pdf_detect
is_run = False
is_pick_up = True
is_on = False
pin_2_state = 0
pin_5_state = 0
SERIAL_PORT = 'COM4' # Replace with your port
BAUD_RATE = 9600
# Single timeout for reading acknowledgments (in seconds)
ACK_TIMEOUT = 5.0
try:
    # For Windows, use "COM3" or the appropriate COM port
    # For Linux, use "/dev/ttyUSB0" or the appropriate port
    robot = MyCobot280("COM3", 115200)
    print("MyCobot initialized successfully.")
except Exception as e:
    print(f"Failed to initialize MyCobot: {e}")
    exit()

def read_json_file(file_path):
    """Reads a JSON file and returns the parsed data."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


base_pick_up = [240.0, -12.9, 91.9, 178.64, -0.67, -50.69]
base_approve = [48.7, -289.2, 91.9, -171.62, -7.79, -129.16]
base_rejected = [33.9, 283.7, 89.5, 176.81, -2.44, 35.89]
async def pump_on():
    try:
        with SerialControl(SERIAL_PORT, BAUD_RATE, timeout=ACK_TIMEOUT) as controller:
            if not controller.ser:
                print("Could not establish serial connection. Exiting.")
                return 

            # --- Test OPEN command ---
            ack = controller.open_pump()
            if ack: # Check if ack is not None
                # Proceed if open was successful
                print(f"Device reported: {ack}")
            else:
                print("Open command failed, cannot proceed.")

        print("\nExited 'with' block, connection automatically closed.")

    except Exception as e:
        # Catch potential errors during __init_s
        print(f"\nAn error occurred: {e}")

# Stop suction pump
async def pump_off( ):
    try:
        with SerialControl(SERIAL_PORT, BAUD_RATE, timeout=ACK_TIMEOUT) as controller:
            if not controller.ser:
                print("Could not establish serial connection. Exiting.")
                return 

            # --- Test OPEN command ---
            ack = controller.close_pump()
            if ack: # Check if ack is not None
                # Proceed if open was successful
                print(f"Device reported: {ack}")
            else:
                print("Open command failed, cannot proceed.")

        print("\nExited 'with' block, connection automatically closed.")

    except Exception as e:
            # Catch potential errors during __init__ or outside command calls
            print(f"\nAn error occurred: {e}")
# async def pump_on():
#     try:
#         # Set pin 5 (G5) to LOW to turn on the suction pump
#         robot.set_basic_output(5, 0)
#         await asyncio.sleep(0.05)  # Wait for the pump to turn on
#         print("Suction pump turned on.")
#     except Exception as e:
#         # Catch potential errors during __init_s
#         print(f"\nAn error occurred: {e}")

# # Stop suction pump
# async def pump_off( ):
#     try:
#         # Set pin 5 (G5) to HIGH to turn off the suction pump
#         robot.set_basic_output(5, 1)
#         await asyncio.sleep(0.05)  # Wait for the pump to start turning off
#         # Set pin 2 (G2) to LOW and then HIGH to ensure the pump is fully off
#         robot.set_basic_output(2, 0)
#         await asyncio.sleep(1)  # Wait for the pump to fully turn off
#         robot.set_basic_output(2, 1)
#         await asyncio.sleep(0.05)  # Wait for the pump to be fully off
#         print("Suction pump turned off.")
#     except Exception as e:
#             # Catch potential errors during __init__ or outside command calls
#             print(f"\nAn error occurred: {e}")


async def setOptions(robot: MyCobot280):
    robot.relase_all_servos()
    while is_run :
        print(robot.get_coords())
        print(robot.get_angles())
        return asyncio.sleep(0.1)  # Yield control to the event loop

async def pick_up_paper(robot: MyCobot280):
    global is_run ,is_pick_up
    is_run = True
    before_pickup = base_pick_up.copy()
    before_pickup[2] = before_pickup[2] + 100
    robot.sync_send_coords(before_pickup,80,timeout=3)
    await pump_on()
    robot.sync_send_coords(base_pick_up,80,timeout=3)
    before_pickup[0]  -= 50
    robot.sync_send_angles([-0, 30, -90, -0, 0, 0], 40)
    base_pick_up[2] = base_pick_up[2] - 0.5
    is_pick_up = True
    is_run = False
            
async def put_paper(robot: MyCobot280, is_accepted: bool):
    global is_run ,is_pick_up
    is_run = True
    before_lev = []
    if is_accepted:
        before_lev = base_approve.copy()
        before_lev[2] = base_approve[2] + 75
        # befoer_approve[2] = befoer_approve[2] + 80
        robot.sync_send_coords(before_lev,80,timeout=4)
        robot.sync_send_coords(base_approve,80,timeout=2)
        base_approve[2] = base_approve[2] + 0.5
    else:
        before_lev = base_rejected.copy()
        before_lev[2] = base_rejected[2]+75
        robot.sync_send_coords(before_lev,80,timeout=4)
        robot.sync_send_coords(base_rejected,80,timeout=2)
        base_rejected[2] = base_rejected[2] + 0.5
    await pump_off()
    print("drop paper.")
    await  asyncio.sleep(0.5)  # Wait for the pump to turn off
    robot.sync_send_coords(before_lev, 80,timeout=3)
    print("drop paper done.")
    is_pick_up = False
    is_run = False

async def update_pin_state():
    global is_on, pin_5_state
    while is_on:
        if pin_5_state != 0:
            robot.set_basic_output(5, pin_5_state)  # Turn on the suction pump
        await asyncio.sleep(0.01)

    
async def main():
    global pin_5_state, is_on
    is_on = True
    robot.power_on()
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) 
    is_run = False
    is_pick_up = False
    is_pdf = False
    is_object = False
    is_contract = False
    scan_count = 0
    robot.sync_send_angles([-0, 30, -90, -0, 0, 0], 80)
    await pick_up_paper(robot)
    await put_paper(robot, True)
    await pick_up_paper(robot)
    await put_paper(robot, False)
    robot.sync_send_angles([-0, 30, -90, -0, 0, 0], 80)
    try:
        while True:
            # ret, image_data = cam.read()
            # if is_pick_up == False:
            #     image,frame_image, is_object, is_pdf, is_contract = pdf_detect.detect_pdf(image_data)
            #     scan_count += 1
            # cv2.imshow("real image", image_data)    # Start capturing frames asynchronously
            # robot.release_all_servos()
            # print(robot.get_coords())
            # await pick_up_paper(robot)
            # if is_run==False:
            #     if is_pdf:
            #        if is_contract or is_pdf and scan_count > 10:
            #             scan_count = 0
            #             if is_pick_up:
            #                 await put_paper(robot, is_contract)
            #             else:
            #                 await pick_up_paper(robot)
            #     if is_object and scan_count > 10:
            #         print("unknown object")
            #         scan_count = 0
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     robot.power_off()
            #     breaks
            # await pump_off(robot)
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
        robot.power_off()
        is_on = False
        await update_task

    cv2.destroyAllWindows()

# Run the asyncio event loop
asyncio.run(main())