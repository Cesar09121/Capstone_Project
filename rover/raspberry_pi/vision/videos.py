import cv2
from flask import Flask, Response
from object_detection import ObjectDetector

app = Flask(__name__)
# Load YOLO detector once at startup
detector = ObjectDetector(confidence=0.5)

# Open default webcam for testing
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        ok, frame = camera.read()

        if not ok:
            break

        # Run YOLO detection
        detections = detector.detect(frame)

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

if __name__ == "__main__":
    print("Video stream running")
    print("http://localhost:5000/video_feed")

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
    )