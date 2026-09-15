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
