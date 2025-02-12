from webBotSocket import MyCobotWebots
import time
import asyncio
import math

doc_read_pos = [0, -0, 0, -68.754935, 0, -90]
doc_pick_pos = [0, -90, 0, 0, 0, -90]
transits_pos = [0, -28.64789, 28.64789, 0, 0, -90]
approve_transits_pos = [90, -28.64789, 28.64789, 0, 0, -90]
approve_pos = [90, -90, 0, 0, 0, -90]
denied_transits_pos = [-90, -0.5, 0.5, 0, 0, -90]
denied_pos = [-90, -90, 0, 0, 0, -90]


async def main():
    mycobot = MyCobotWebots()
    await mycobot.power_on()
    await mycobot.send_angles(doc_read_pos)
    time.sleep(3)
    await mycobot.get_image()
    time.sleep(2)
    await mycobot.send_angles(doc_pick_pos)
    time.sleep(3)
    await mycobot.send_angles(transits_pos)
    time.sleep(3)
    await mycobot.send_angles(approve_pos)
    time.sleep(3)
    await mycobot.send_angles(denied_pos)
    time.sleep(3)
    await mycobot.power_off()


if __name__ == "__main__":
    mycobot = MyCobotWebots()
    asyncio.run(main())
    
     