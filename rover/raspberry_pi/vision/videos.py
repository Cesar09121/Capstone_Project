import cv2
from flask import Flask, Response, jsonify
from object_detection import ObjectDetector

latest_detection=[]

app = Flask(__name__)
# Load YOLO detector once at startup
detector = ObjectDetector(confidence=0.5)

# Open default webcam for testing
camera = cv2.VideoCapture(0)

def generate_frames():
    global latest_detections

    while True:
        ok, frame = camera.read()

        if not ok:
            break

        # Run object detection
        detections = detector.detect(frame)
        print(detections)

        # Save latest YOLO results
        latest_detections = detections

        # Draw detection boxes
        frame = detector.draw(frame, detections)

        # Convert frame to JPEG
        ok, buffer = cv2.imencode(".jpg", frame)

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
    print("Video stream running")
    print("http://localhost:5000/video_feed")

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
    )