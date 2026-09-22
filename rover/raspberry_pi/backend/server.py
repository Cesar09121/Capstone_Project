import asyncio
import json
import math
import random
import time
import websockets
import urllib.request


def get_yolo_detections():
    try:
        with urllib.request.urlopen(
            "http://localhost:5000/detections",
            timeout=0.2,
        ) as response:
            return json.loads(response.read().decode())
    except Exception:
        return []

# Generate the mock rover telemetry
def get_mock_rover_data():
    t = time.time()

    def jitter():
        value = (
            60
            + math.sin(t * 2) * 40
            + random.uniform(-10, 10)
        )
        return max(0, round(value))

    return {
        "connected": True,
        "controllerConnected": True,
        "rgbCameraConnected": True,
        "thermalCameraConnected": True,
        "mode": "DRIVE",
        "wheels": {
            "FL": jitter(),
            "FR": jitter(),
            "RL": jitter(),
            "RR": jitter(),
        },
        "drivers": {
            "MDD10A_1": "OK",
            "MDD10A_2": "OK",
        },
        "battery": round(random.uniform(12.4, 12.8), 1),
        "detections": get_yolo_detections()
    }

# Send the data to the frontend
async def send_rover_data(websocket):
    print("Dashboard connected")

    try:
        while True:
            data = get_mock_rover_data()

            await websocket.send(json.dumps(data))

            await asyncio.sleep(0.4)

    except websockets.ConnectionClosed:
        print("Dashboard disconnected")

# Start the WebSocket server
async def main():
    async with websockets.serve(
        send_rover_data,
        "localhost",
        8765,
    ):
        print("WebSocket server running")
        print("ws://localhost:8765")

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())