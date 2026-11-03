"""
Benchmark YOLOv8-nano with different image sizes and confidence scores.
It captures a fixed set of camera frames first, so every setting is tested
on the same images. Results are printed as a table and saved to a CSV file.
"""
import csv
import time
import cv2
from object_detection import ObjectDetector

# Laptop webcam: 0
CAMERA_SOURCE = 0

# Settings to test
IMAGE_SIZES = [640, 416, 320, 288, 256]
CONFIDENCES = [0.25, 0.4, 0.5, 0.6]

NUM_FRAMES = 30   # frames tested for each setting
WARMUP_RUNS = 3   # untimed runs after each image size change

RESULTS_FILE = "benchmark_results.csv"

# Capture the test frames once
def capture_frames():
    if isinstance(CAMERA_SOURCE, str):
        camera = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_V4L2)
    else:
        camera = cv2.VideoCapture(CAMERA_SOURCE)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():
        print("Could not open camera.")
        return []

    # Skip the first frames while the camera adjusts its exposure
    for _ in range(10):
        camera.read()

    frames = []
    while len(frames) < NUM_FRAMES:
        ok, frame = camera.read()

        if ok:
            frames.append(frame)

    camera.release()
    return frames

# Test one image size + confidence on all frames
def run_test(detector, frames, imgsz, confidence):
    detector.imgsz = imgsz
    detector.confidence = confidence

    # Warm up so the first slow run is not counted
    for i in range(WARMUP_RUNS):
        detector.detect(frames[i % len(frames)])

    times = []
    total_detections = 0
    total_confidence = 0.0

    for frame in frames:
        start = time.time()
        detections = detector.detect(frame)
        times.append(time.time() - start)

        total_detections += len(detections)
        total_confidence += sum(det["confidence"] for det in detections)

    avg_ms = sum(times) / len(times) * 1000

    return {
        "imgsz": imgsz,
        "confidence": confidence,
        "avg_ms": round(avg_ms, 1),
        "fps": round(1000 / avg_ms, 1),
        "detections_per_frame": round(total_detections / len(frames), 2),
        "avg_detection_confidence": round(total_confidence / total_detections, 2) if total_detections else 0,
    }

def main():
    print(f"Capturing {NUM_FRAMES} test frames...")
    frames = capture_frames()

    if not frames:
        return

    # Load the model once and change its settings for each test
    detector = ObjectDetector()

    results = []
    print()
    print(f"{'imgsz':>6} {'conf':>6} {'avg ms':>8} {'fps':>6} {'det/frame':>10} {'avg conf':>9}")

    for imgsz in IMAGE_SIZES:
        for confidence in CONFIDENCES:
            result = run_test(detector, frames, imgsz, confidence)
            results.append(result)

            print(
                f"{result['imgsz']:>6} "
                f"{result['confidence']:>6} "
                f"{result['avg_ms']:>8} "
                f"{result['fps']:>6} "
                f"{result['detections_per_frame']:>10} "
                f"{result['avg_detection_confidence']:>9}"
            )

    # Save the results for the report
    with open(RESULTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"Saved results to {RESULTS_FILE}")


if __name__ == "__main__":
    main()