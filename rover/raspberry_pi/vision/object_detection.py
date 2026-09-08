"""
Real-time object detection for the rover's RGB camera using YOLOv8-nano.
For now, this runs on the laptop webcam for testing.
Later, it can be moved into the Raspberry Pi vision system.
"""
import cv2 # handles camera and drawing
from ultralytics import YOLO
class ObjectDetector:
    # Loads YOLOv8-nano model, only reports detection if confidence >= 50%
    def __init__(self, model_path="yolov8n.pt", confidence=0.5):
        # Nano is used because it is lightweight and better for Raspberry Pi later.
        self.model = YOLO(model_path)
        self.confidence = confidence

    def detect(self, frame):
        """
        Detect objects in one camera frame.
        Returns:
        [
            {
                "label": object name,
                "confidence": confidence score,
                "box": (x1, y1, x2, y2)
            }
        ]
        """
        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False
        )

        detections = []

        for result in results:
            for box in result.boxes:

                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                conf = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append({"label": label,
                                  "confidence": conf,
                                  "box": (int(x1),
                                          int(y1),
                                          int(x2),
                                          int(y2)
                    ),
                })

        return detections

    def draw(self, frame, detections):
        # Draw bounding boxes and labels on the frame
        # Mainly used for laptop testing
        
        for det in detections:
            x1, y1, x2, y2 = det["box"]

            label = (
                f'{det["label"]} '
                f'{det["confidence"]:.2f}'
            )
            cv2.rectangle(frame,
                         (x1, y1),
                         (x2, y2),
                         (0, 255, 0),
                          2
            )
            cv2.putText(frame,
                        label,
                        (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
            )
        return frame

def run_standalone():
    # Test object detection using the laptop webcam
    detector = ObjectDetector()

    # 0 means the default webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open webcam.")
        return
    print("Running object detection.")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        # Detect objects
        detections = detector.detect(frame)
        # Draw the detected objects
        frame = detector.draw(
            frame,
            detections
        )
        # Show the camera preview
        cv2.imshow(
            "Rover Object Detection",
            frame
        )
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()

# opens your laptop webcam, sends frames into YOLO and displays the detections live
if __name__ == "__main__":
    run_standalone()
