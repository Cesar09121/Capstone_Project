import asyncio
import json
import math
import random
import time
import websockets
import urllib.request
import threading

# Use "localhost" for laptop webcam, Pi IP for rover camera
VIDEO_HOST = "localhost"

def get_yolo_detections():
    try:
        with urllib.request.urlopen(
            f"http://{VIDEO_HOST}:5001/detections",
            timeout=0.2,
        ) as response:
            return json.loads(response.read().decode())
    except Exception:
        return []

# Thermal Camera
THERMAL_WIDTH = 32
THERMAL_HEIGHT = 24
 
latest_thermal = []
mlx = None
# Try to open the real MLX90640, fall back to mock data if not found
try:
    import board
    import busio
    import adafruit_mlx90640
 
    i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
    mlx = adafruit_mlx90640.MLX90640(i2c)
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
    print("MLX90640 connected")
 
except Exception as e:
    print("Thermal camera not found, using mock data:", e)

# Room temperature background with a warm moving blob
def get_mock_thermal():
    t = time.time()
    cx = 16 + math.sin(t * 0.8) * 10
    cy = 12 + math.cos(t * 0.6) * 6
 
    pixels = []
    for y in range(THERMAL_HEIGHT):
        for x in range(THERMAL_WIDTH):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            value = (
                22
                + 12 * math.exp(-(dist ** 2) / 20)
                + random.uniform(-0.3, 0.3)
            )
            pixels.append(round(value, 1))
 
    return pixels

# Keep reading thermal frames in the background
def read_thermal_loop():
    global latest_thermal
    frame = [0.0] * (THERMAL_WIDTH * THERMAL_HEIGHT)
 
    while True:
        if mlx is None:
            latest_thermal = get_mock_thermal()
            time.sleep(0.25)
            continue
 
        try:
            mlx.getFrame(frame)
            latest_thermal = [round(v, 1) for v in frame]
        except ValueError:
            # Occasional bad I2C read, keep the last good frame
            pass
 
# Package thermal data for the dashboard
def get_thermal_data():
    pixels = latest_thermal
 
    return {
        "width": THERMAL_WIDTH,
        "height": THERMAL_HEIGHT,
        "pixels": pixels,
        "min": min(pixels) if pixels else 0,
        "max": max(pixels) if pixels else 0,
    }

# Generate the mock rover telemetry
def get_mock_rover_data(detections):
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
        "detections": detections,
        "thermal": get_thermal_data()
    }

# Send the data to the frontend
async def send_rover_data(websocket):
    print("Dashboard connected")

    try:
        while True:
            detections = await asyncio.to_thread(get_yolo_detections)

            data = get_mock_rover_data(detections)

            await websocket.send(json.dumps(data))

            await asyncio.sleep(0.4)

    except websockets.ConnectionClosed:
        print("Dashboard disconnected")

# Start the WebSocket server
async def main():
    threading.Thread(target=read_thermal_loop, daemon=True).start()
    
    async with websockets.serve(
        send_rover_data,
        "0.0.0.0",
        8765,
    ):
        print("WebSocket server running")
        print("ws://localhost:8765")

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())