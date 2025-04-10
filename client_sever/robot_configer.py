from pymycobot import MyCobot280
try:
    # For Windows, use "COM3" or the appropriate COM port
    # For Linux, use "/dev/ttyUSB0" or the appropriate port
    robot = MyCobot280("COM3", 115200)
    print("MyCobot initialized successfully.")
except Exception as e:
    print(f"Failed to initialize MyCobot: {e}")
    exit()


if __name__ == "__main__":
    # off the robot
    robot.power_on()
    robot.release_all_servos()
    while True:
        try:
            # get the position of the robot
            print(robot.get_coords())
        except KeyboardInterrupt:
            print("Exiting...")
            break
    