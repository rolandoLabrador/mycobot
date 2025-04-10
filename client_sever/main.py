#from webBotSocket import MyCobotWebots
from pymycobot import MyCobot280
import cv2
import numpy as np
import asyncio
import json
import time
import pdf_detect
is_run = False
is_pick_up = True
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


base_pick_up = [155.7, -204.9, 86.1, -177.37, -0.5, -55.53]
base_approve =  [260.6, 104.1, 89.3, -177.42, 1.41, -33.24]
base_rejected = [-202.5, -193.1, 91.7, 178.66, -2.59, 169.22]
[104.6, -165.9, 189.8, -167.38, -12.86, -85.89]
async def pump_on(robot):
    try:
        # Set pin 5 (G5) to LOW to turn on the suction pump
        robot.set_basic_output(5, 0)
        await asyncio.sleep(0.05)  # Wait for the pump to turn on
        print("Suction pump turned on.")
    except Exception as e:
        print(f"Failed to turn on pump: {e}")

# Stop suction pump
async def pump_off(robot:MyCobot280):
    try:
        # Set pin 5 (G5) to HIGH to turn off the suction pump
        robot.set_basic_output(5, 1)
        await asyncio.sleep(0.05)  # Wait for the pump to start turning off
        # Set pin 2 (G2) to LOW and then HIGH to ensure the pump is fully off
        robot.set_basic_output(2, 0)
        await asyncio.sleep(1)  # Wait for the pump to fully turn off
        robot.set_basic_output(2, 1)
        await asyncio.sleep(0.05)  # Wait for the pump to be fully off
        print("Suction pump turned off.")
    except Exception as e:
        print(f"Failed to turn off pump: {e}")


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
    before_pickup[2] = before_pickup[2] + 80
    before_pickup[1] = before_pickup[1] + 40
    before_pickup[0] = before_pickup[0] - 40    
    robot.sync_send_coords(before_pickup,80,timeout=3)
    await pump_on(robot)
    robot.sync_send_coords(base_pick_up,80,timeout=3)
    space_pos = base_pick_up.copy()
    space_pos[2] = space_pos[2] + 60
    robot.sync_send_coords(space_pos,80,timeout=1)
    robot.sync_send_coords(before_pickup,80,timeout=3)
    base_pick_up[2] = base_pick_up[2] - 0.5
    is_pick_up = True
    is_run = False
            
async def put_paper(robot: MyCobot280, is_accepted: bool):
    global is_run ,is_pick_up
    is_run = True
    before_lev = []
    if is_accepted:
        before_lev = base_approve.copy()
        before_lev[2] = base_approve[2] + 80
        # befoer_approve[2] = befoer_approve[2] + 80
        robot.sync_send_coords(before_lev,80,timeout=3)
        robot.sync_send_coords(base_approve,80,timeout=3)
        base_approve[2] = base_approve[2] + 0.5
    else:
        before_lev = base_rejected.copy()
        before_lev[2] = base_rejected[2]+80
        robot.sync_send_coords(before_lev,80,timeout=3)
        robot.sync_send_coords(base_rejected,80,timeout=3)
        base_rejected[2] = base_rejected[2] + 0.5
    await pump_off(robot)
    robot.sync_send_coords(before_lev, 80,timeout=3)
    is_pick_up = False
    is_run = False
    
async def main():
    robot.power_on()
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) 
    is_run = False
    is_pick_up = False
    is_pdf = False
    is_object = False
    is_contract = False
    scan_count = 0
    robot.set_basic_output(2, 0)  # Set pin 2 (G2) to HIGH


    
    robot.sync_send_angles([-45, 30, -90, -0, 0, 0], 80)
    await pick_up_paper(robot)
    await put_paper(robot, True)
    await pick_up_paper(robot)
    await put_paper(robot, False)
    robot.sync_send_angles([-45, 30, -90, -0, 0, 0], 80)
    while True:
        ret, image_data = cam.read()
        if is_pick_up == False:
            image,frame_image, is_object, is_pdf, is_contract = pdf_detect.detect_pdf(image_data)
            scan_count += 1
        cv2.imshow("real image", image_data)    # Start capturing frames asynchronously
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
        if cv2.waitKey(1) & 0xFF == ord('q'):
            robot.power_off()
            break

    cv2.destroyAllWindows()

# Run the asyncio event loop
asyncio.run(main())