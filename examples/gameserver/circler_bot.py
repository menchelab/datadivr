# run multiple bots that fly in a circle around Vienna.


import asyncio
import json
import math
import time
from contextlib import suppress

import websockets

VIENNA_CENTER = (48.2082, 16.3738)
BRATISLAVA_CENTER = (48.1486, 17.1077)
UPDATE_INTERVAL = 0.2  # 200ms between updates
WS_URI = "ws://jetskeee.com:8765/ws"


class CircleBot:
    def __init__(self, name, radius_km, speed_deg_per_sec, center=VIENNA_CENTER, altitude=1000):
        self.name = name
        self.radius_km = radius_km
        self.speed_deg_per_sec = speed_deg_per_sec
        self.center = center
        self.altitude = altitude
        self.start_time = None

    async def start(self, websocket):
        self.start_time = time.time()
        await websocket.send(
            json.dumps({"event_name": "GAMESERVER_SET_NAME", "to": "others", "payload": {"name": self.name}})
        )

    def calculate_position(self, elapsed_time):
        angle_deg = (elapsed_time * self.speed_deg_per_sec) % 360
        angle_rad = math.radians(angle_deg)

        lat = self.center[0] + (self.radius_km / 111) * math.cos(angle_rad)
        lon = self.center[1] + (self.radius_km / (111 * math.cos(math.radians(self.center[0])))) * math.sin(angle_rad)
        direction = (angle_deg + 90) % 360

        return lat, lon, direction


async def run_bot(bot):
    while True:  # Outer loop for reconnection
        try:
            async with websockets.connect(WS_URI, ping_interval=20, ping_timeout=60) as websocket:
                print(f"Connected to {WS_URI} for {bot.name}")
                await bot.start(websocket)

                while True:
                    receive_task = asyncio.create_task(websocket.recv())
                    send_task = asyncio.create_task(send_update(bot, websocket))

                    # Wait for either task to complete
                    done, pending = await asyncio.wait([receive_task, send_task], return_when=asyncio.FIRST_COMPLETED)

                    # Cancel pending tasks
                    for task in pending:
                        task.cancel()

                    # Process completed tasks
                    for task in done:
                        with suppress(asyncio.CancelledError):
                            await task

                    await asyncio.sleep(UPDATE_INTERVAL)

        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed for {bot.name}, attempting to reconnect...")
            await asyncio.sleep(5)  # Wait before reconnecting
        except Exception as e:
            print(f"Error for {bot.name}: {e}")
            await asyncio.sleep(5)


async def send_update(bot, websocket):
    """Helper function to send position updates"""
    current_time = time.time()
    elapsed_time = current_time - bot.start_time
    lat, lon, direction = bot.calculate_position(elapsed_time)

    message = {
        "event_name": "GAMESERVER_INFO_UPDATE",
        "to": "others",
        "payload": {"latitude": lat, "longitude": lon, "altitude": bot.altitude, "direction": direction},
    }

    await websocket.send(json.dumps(message))
    if int(elapsed_time) % 5 == 0:  # Print every 5 seconds
        print(f"{bot.name} - Position: {lat:.4f}, {lon:.4f}, Direction: {direction:.1f}°")


async def run_bots(bots):
    tasks = [run_bot(bot) for bot in bots]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    bots = [
        CircleBot("Fast Observer", radius_km=50, speed_deg_per_sec=360 / 10),  # Complete circle in 10 seconds
        CircleBot("Slow Observer", radius_km=25, speed_deg_per_sec=360 / 30),
        CircleBot("High Altitude Observer", radius_km=40, speed_deg_per_sec=360 / 20),
        CircleBot("Euro Fighter", radius_km=110, speed_deg_per_sec=360 / 5),
        CircleBot("High Speed Ringbahn", radius_km=0.8, speed_deg_per_sec=360 / 10),
    ]

    for bot in bots:
        print(f"Bot: {bot.name}, Radius: {bot.radius_km}km, Speed: {bot.speed_deg_per_sec:.1f}°/s")

    asyncio.run(run_bots(bots))
