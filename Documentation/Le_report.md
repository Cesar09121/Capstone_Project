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
