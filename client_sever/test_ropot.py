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



if __name__ == "__main__":
    # Initialize the robot and set options
    robot.power_on()
    robot.release_all_servos()
    robot.set_basic_output(5,0)  # Turn on the suction pump
    for i in range(5):
        robot.set_basic_output(5,1)  # Turn on the suction pump
    robot.power_off()