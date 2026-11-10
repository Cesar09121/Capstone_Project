# Week 1

Implemented a standalone YOLOv8-nano object detection prototype using Python and OpenCV. It reads live webcam frames, performs object detection, and returns structured labels, confidence scores, and bounding boxes. The detection class is designed so it can later be reused in the Raspberry Pi vision pipeline.

## Object Detection Flow

Laptop (captures live webcam frames) -> OpenCV read frames -> YOLOv8-nano object detection -> Structured labels, confidence scores, and bounding boxes -> OpenCV display

### Output example

{
"label": "person",
"confidence": 0.87,
"box": (x1, y1, x2, y2)
}

## React Rover Dashboard Prototype

Created a React-based rover dashboard prototype. The interface currently contains

- Placeholders for the RGB camera
- A simulated MLX90640 thermal heatmap
- Simulated four-wheel RPM telemetry
- Motor-driver status
- Controller status
- Battery voltage
- Rover mode
  The frontend currently uses mock data so the user interface can be developed before the physical hardware is connected.

  The next step is to build the Python backend communication layer and connect the backend to the React dashboard. After that, the simulated data will gradually be replaced by real Raspberry Pi, camera, thermal sensor, and Arduino telemetry data.

# Week 2

Implemented the Python backend communication layer and connected it to React rover dashboard through webSocket. The current backend generates simulated rover telemetry and sends the data to the frontend as JSON. The React dashboard receives the data and updates the displayed values in real time.

## Backend/WebSocket Communication flow

Python backend -> Generate Mock rover telemetry -> JSON -> WebSocket -> React frontend

### Next step

The next step is to begin replacing simulated backend data with real subsystem data from the Raspberry Pi, RGB camera, thermal sensor, and Arduino telemetry.

# Week 3

Integrated the real RGB camera and YOLO object detection into the React rover dashboard.

A new Flask video server was created to capture frames from the camera using OpenCV, run YOLO object detection, draw bounding boxes and confidence scores, encode the annotated frames as JPEG images, and stream them to the React dashboard using MJPEG.

## RGB Camera / YOLO Flow

RGB Camera -> OpenCV -> YOLO -> Bounding Boxes + Confidence -> MJPEG Stream -> React Dashboard
The previous fake RGB placeholder in the dashboard was replaced with a real live camera stream.

## YOLO Detection Data

A `/detections` endpoint was added to the Flask server to provide structured YOLO detection results as JSON.
Each detection now includes:

- object label
- confidence score
- bounding box coordinates

Example:
{
"label": "person",
"confidence": 0.75,
"box": [x1, y1, x2, y2]
}

### Next Step

The next step is to move the Python camera, YOLO, and backend services from the laptop to the Raspberry Pi 5 and test them with the real rover USB camera.

# Week 4

Integrated the RGB camera from the Raspberry Pi into the React rover dashboard.
The Raspberry Pi now runs the RGB camera and object-detection pipeline, and the live video stream is displayed directly in the dashboard.

## RGB Camera Flow

RGB Camera -> Raspberry Pi -> OpenCV -> YOLO Object Detection -> MJPEG Video Stream -> React Dashboard

### Next Step

The next step is to integrate the thermal sensor and Arduino telemetry into the React rover dashboard, replacing the remaining simulated data with real hardware inputs.

# Week 5

Integrated the Thermal camera from the Raspberry Pi into the React rover dashboard.
The Raspberry Pi now runs the thermal sensor and generates a heatmap, which is displayed directly in the dashboard.

## Thermal Camera Flow

Thermal Sensor -> Raspberry Pi -> Heatmap Generation -> React Dashboard

### Next Step

Creating benchmark for optimal performance of the thermal sensor and RGB camera integration on the Raspberry Pi.

# Week 6

Optimized the RGB camera video stream on the Raspberry Pi to reduce lag, based on the midterm feedback to fix video streaming for the CV pipeline.

- Added a background thread that continuously reads the camera and keeps only the newest frame, so YOLO always processes the current frame instead of a backlog of old frames
- Set the camera buffer size to 1 and the resolution to 640x480
- Reduced the JPEG quality to 70 so each frame is smaller to send over Wi-Fi
- Reduced the YOLO input size (imgsz) from 640 to 288 pixels for faster detection on the Raspberry Pi
- Added an FPS print to measure detection speed

## Flow

RGB Camera -> Background Capture Thread (newest frame only) -> YOLO (imgsz=288) -> MJPEG Stream (JPEG quality 70) -> React Dashboard

## Result

Laptop: YOLO runs at about 27-28 FPS, keeping up with the camera
Raspberry Pi: the video stream is faster and no longer falls seconds behind; YOLO runs at about 13 FPS at imgsz=288

### Next Step

Improve the thermal camera update speed on the Raspberry Pi by increasing the I2C bus speed and the sensor refresh rate, and then continue finalizing the operator dashboard.

# Week 7

Improved the thermal camera update speed on the Raspberry Pi and created benchmark scripts to test and optimize both the thermal camera and the RGB object detection

- Increased the I2C bus speed to 400 kHz in /boot/firmware/config.txt (dtparam=i2c_arm_baudrate=400000)
- Increased the MLX90640 refresh rate from 4 Hz to 8 Hz
- Handled more I2C read errors (RuntimeError, OSError) so one bad read does not stop the thermal thread
- Reduced the WebSocket send interval from 0.4 s to 0.25 s
- Added an FPS print to measure the thermal speed

## Thermal Camera Flow

Thermal Sensor -> I2C (400 kHz) -> Raspberry Pi (8 Hz, 768 temperatures) -> WebSocket (every 0.25 s) -> React Dashboard (heatmap)

## Thermal Benchmark

![](./images/thermal_benchmark.png)
Selected setting: 8 Hz, which gives 3.9 FPS (2x faster than before) and matches the 0.25 s WebSocket send interval.

## RGB Benchmark

The benchmark captures 30 frames from the camera and tests every combination of YOLO image size (640, 416, 320, 288, 256) and confidence score (0.25, 0.4, 0.5, 0.6) on the same frames.

![](./images/rgb_benchmark.png)

Selected settings: imgsz=288 and confidence=0.5, which gives about 13 FPS with reliable detections.

## Next Step

The next step is to finalize the operator dashboard: add automatic WebSocket reconnection, make the status indicators show the real connection state, display the YOLO detection list, and replace the remaining mock telemetry with real Arduino data once the drive system is ready.

# Week 8

Finalized the reliability of the operator dashboard, based on the midterm feedback to finalize the laptop operator display.
Previously, the dashboard only connected to the backend once, when the page loaded. If the backend restarted, the dashboard stayed "Offline" until the page was refreshed. The status indicators were also hardcoded, so they always showed "Connected" even when a camera was not working.

## Changes

- Reconnect to the backend automatically every 2 s after a disconnect
- RGB and thermal status dots now show the real connection state
- Show "Waiting for camera..." when the video server is offline
- Show YOLO detections (label, confidence, position) under the video
- Set the rover IP in one place (ROVER_HOST)

## Testing

- The detection list updates live under the video
- Stopping the backend shows all systems as offline; restarting it reconnects automatically
- Stopping the video server shows "Waiting for camera..." and a red RGB status, while the thermal feed keeps working

## Next Step

The next step is to prepare the dashboard for real hardware data: detect the PS5 controller connection on the Raspberry Pi, and add an Arduino serial reader for real wheel RPMs once the drive system is ready.
