import cv2
import threading
import time
from flask import Flask, Response, jsonify
from object_detection import ObjectDetector

# Laptop webcam: 0
CAMERA_SOURCE = 0

latest_detections=[]
latest_frame = None
latest_annotated = None

app = Flask(__name__)
# Load YOLO detector once at startup
detector = ObjectDetector(confidence=0.5)

# Open the camera (a device path needs the V4L2 backend on the Pi)
if isinstance(CAMERA_SOURCE, str):
    camera = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_V4L2)
else:
    camera = cv2.VideoCapture(CAMERA_SOURCE)

# Smaller frames for less work and less data over Wi-Fi
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# Keep only the newest frame in the camera buffer
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Keep grabbing frames so we always have the newest one
def capture_loop():
    global latest_frame

    while True:
        ok, frame = camera.read()

        if not ok:
            time.sleep(0.01)
            continue

        latest_frame = frame

# Run YOLO on the newest frame only, skip any frames it missed
def detection_loop():
    global latest_detections, latest_annotated

    last_frame = None
    frames = 0
    start = time.time()

    while True:
        frame = latest_frame

        # Wait for a new frame instead of detecting the same one twice
        if frame is None or frame is last_frame:
            time.sleep(0.005)
            continue

        last_frame = frame

        # Run object detection
        detections = detector.detect(frame)

        # Save latest YOLO results
        latest_detections = detections

        # Draw detection boxes
        latest_annotated = detector.draw(frame.copy(), detections)

        # Print the detection speed every 5 seconds
        frames += 1
        elapsed = time.time() - start

        if elapsed >= 5:
            print(f"YOLO: {frames / elapsed:.1f} fps")
            frames = 0
            start = time.time()

def generate_frames():
    last_sent = None

    while True:
        frame = latest_annotated
        # Only send a frame when there is a new one
        if frame is None or frame is last_sent:
            time.sleep(0.01)
            continue

        last_sent = frame

        # Convert frame to JPEG (quality =70)
        ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ok:
            continue

        frame_bytes = buffer.tobytes()
        # Send frame as MJPEG stream
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )

@app.route("/detections")
def detections():
    return jsonify(latest_detections)

if __name__ == "__main__":
    threading.Thread(target=capture_loop, daemon=True).start()
    threading.Thread(target=detection_loop, daemon=True).start()

    print("Video stream running")
    #print("http://localhost:5001/video_feed")
    print("http://192.168.1.175:5001/video_feed")

    app.run(
        host="0.0.0.0",
        port=5001,
        threaded=True,
    )
