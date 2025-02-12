import asyncio
import websockets
import json
import base64
from controller import Robot
import numpy as np
import cv2 
# Webots robot controller setup\
robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())

# Initialize motors (adjust names based on your Webots MyCobot simulation)
motors = []
postion_sensor = []
motor_names = ["joint2_to_joint1", "joint3_to_joint2", "joint4_to_joint3", "joint5_to_joint4", "joint6_to_joint5", "joint6output_to_joint6"]
motor_sensor_name= ["joint2_to_joint1_sensor","joint3_to_joint2_sensor","joint4_to_joint3_sensor","joint5_to_joint4_sensor","joint6_to_joint5_sensor","joint6output_to_joint6_sensor"]
for name in motor_names:
    motor = robot.getDevice(name)
    motor.setVelocity(1)
    motors.append(motor)

for name in motor_sensor_name:
    sensor = robot.getDevice(name)
    postion_sensor.append(sensor)
    
camera = robot.getDevice("camera")
camera.enable(TIME_STEP)
gripper = robot.getDevice("vacuum gripper")


# Function to set joint angles
def set_joint_angles(angles):
    for i, angle in enumerate(angles):
        motors[i].setPosition(angle)

def capture_image():
    try : 
        image = np.frombuffer(camera.getImage(), dtype=np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
        rgb_image = image[:, :, :3]
        # Encode the RGB image as base64
        _, encoded_image = cv2.imencode('.jpg', rgb_image)
        return base64.b64encode(encoded_image).decode('utf-8')
    except Exception as e :
        print(e)
        return None
    # Function to send image data in chunks
async def send_image_in_chunks(websocket):
    image_data = capture_image()
    if image_data:
        CHUNK_SIZE = 1024  # Define the chunk size (1 KB here)
        for i in range(0, len(image_data), CHUNK_SIZE):
            chunk = image_data[i:i + CHUNK_SIZE]
            await websocket.send(chunk)
        # Send an "END" signal to indicate the transmission is complete
        await websocket.send("END")
    else:
        await websocket.send(json.dumps({"status": "error", "message": "No image data available"}))

# Function to handle incoming WebSocket messages
async def handle_message(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
            if data["type"] == "joint_angles":
                angles = data["angles"]
                set_joint_angles(angles)
                await websocket.send(json.dumps({"status": "success", "message": "Joint angles updated"}))

            elif data["type"] == "position":
                # Placeholder: Implement position control if needed
                await websocket.send(json.dumps({"status": "error", "message": "Position control not implemented"}))
                
            elif data["type"] == "get_image":
                print('getImage')
                await send_image_in_chunks(websocket)

            elif data["type"] == "power":
                state = data["state"]
                if state:
                    print("Powering on the robot")
                else:
                    print("Powering off the robot")
                await websocket.send(json.dumps({"status": "success", "message": "Power state updated"}))

            else:
                await websocket.send(json.dumps({"status": "error", "message": "Unknown command type"}))

        except Exception as e:
            error_message = {"status": "error", "message": str(e)}
            await websocket.send(json.dumps(error_message))

# Start the WebSocket server
async def main():
    print("Starting Webots WebSocket server on ws://localhost:12345...")
    # Start the WebSocket server
    server = await websockets.serve(handle_message, "localhost", 12345)
    
    # Keep the simulation running
    while robot.step(TIME_STEP) != -1:
        await asyncio.sleep(0.01)  # Allow the event loop to process WebSocket messages

    # Cleanup when the simulation ends
    server.close()
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())