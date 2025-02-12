import asyncio
import websockets
import json
import time
import base64
from PIL import Image
from io import BytesIO
import math

class MyCobotWebots:

    def __init__(self ,websocket_url = "ws://localhost:", port = 12345):
        self.WEBSOCKET_URL = websocket_url + str(port)
        

    # Example control commands for the MyCobot robot
    async def send_angles(self,angles, speed=10):
        request = {
            "type": "joint_angles",
            "speed": math.radians(speed),  # Example: 10
            "angles": [math.radians(angle) for angle in angles]  # Example: [0, 45, 90, 0, 45, 0]
        }
        return await self.send_command(request)
    
    async def send_angle(self,id,degree,speed = 10):
        request = {
            "type": "joint_angle",
            "id": id,
            "speed": math.radians(speed),  # Example: 10
            "angle": math.radians(degree)  # Example: [0, 45, 90, 0, 45, 0]
        }
        return await self.send_command(request)
    
    # get_angles()

    async def get_angles(self):
        request = {
            "type": "get_joint_angles"
        }
        data = await self.send_command(request)
        return [math.degrees(angle) for angle in data['angles']]
    
    
    # get_coords()

    async def get_coords(self):
        request = {
            "type": "get_coords"
        }
        data = await self.send_command(request)
        return data['coords']
    
    # send_coord(id, coord, speed)

    async def send_coord(self,id,coord,speed = 10):
        request = {
            "type": "coord",
            "id": id,
            "coord": coord,  # Example: [200, 0, 250, 0, 0, 0]
            "speed": speed
        }
        return await self.send_command(request)
    
    # send_coords(coords, speed, mode)

    async def send_coords(self,coords,speed = 10,mode = 0):
        request = {
            "type": "coords",
            "coords": coords,  # Example: [200, 0, 250, 0, 0, 0]
            "speed": speed,
            "mode": mode
        }
        return await self.send_command(request)
    
    # sync_send_angles(angles, speed)

    async def sync_send_angles(self,angles,speed = 10):
        request = {
            "type": "sync_joint_angles",
            "speed": speed,  # Example: 10
            "angles": angles  # Example: [0, 45, 90, 0, 45, 0]
        }
        return await self.send_command(request)
    
    # sync_send_coords(coords, speed, mode)
    
    async def sync_send_coords(self,coords,speed = 10,mode = 0):
        request = {
            "type": "sync_coords",
            "coords": coords,  # Example: [200, 0, 250, 0, 0, 0]
            "speed": speed,
            "mode": mode
        }
        return await self.send_command(request)

    async def power_on(self):
        request = {
            "type": "power",
            "state": 1  # True for power on, False for power off
        }
        return await self.send_command(request)
        
    
    async def power_off(self):
        request = {
            "type": "power",
            "state": 0  # True for power on, False for power off
        }
        return await self.send_command(request)

    async def get_image(self):
        command = {
            "type": "get_image"
        }
        async with websockets.connect(self.WEBSOCKET_URL) as websocket:
            await websocket.send(json.dumps(command))
            image_chunks = []
            while True:
                chunk = await websocket.recv()
                if chunk == "END":  # End of transmission
                    break
                image_chunks.append(chunk)

            # Combine chunks and decode image
            image_data = base64.b64decode("".join(image_chunks))

            image = Image.open(BytesIO(image_data))
            image.show()
            print("Image displayed successfully.")

    async def send_command(self,command):
        async with websockets.connect(self.WEBSOCKET_URL) as websocket:
            await websocket.send(json.dumps(command))
            response = await websocket.recv()
            print("Response:", response)
            return response

async def test_main():
    webSocketWebots  = MyCobotWebots()
    try:
        print("Connecting to Webots WebSocket server...")
        await webSocketWebots.power_on()
        time.sleep(1)

        # Move to a specific joint configuration
        await webSocketWebots.send_angles([0, -0, 0, -1.2, 0, -1.57079])
        time.sleep(1)

        # Request an image from the server
        await webSocketWebots.get_image()

        # Power off the robot
        await webSocketWebots.power_off()

        # Power on the robot
        
    except Exception as e:
        print("An error occurred:", e)

# Run the main async function
if __name__ == "__main__":
    asyncio.run(test_main())
    
