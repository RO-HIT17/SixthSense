import cv2
import numpy as np
import pyttsx3
import time
from ultralytics import YOLO

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speaking speed

# Load custom YOLOv8 model
model = YOLO("yolov8n.pt")

# Known object widths in cm
KNOWN_WIDTHS = {
    "person": 40, "bicycle": 65, "car": 150, "motorbike": 70, "bus": 250,
    "truck": 250, "chair": 100, "laptop": 40, "cell phone": 15
}

FOCAL_LENGTH = 500  # Adjust based on calibration
CRITICAL_DISTANCE = 50  # Distance threshold in cm

cap = cv2.VideoCapture(1)  # Use external camera
last_update_time = time.time()
distance_results = {}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Perform object detection
    results = model(frame)
    detected_objects = {}
    warnings = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = model.names[int(box.cls[0])]
            confidence = box.conf[0].item()

            if label not in KNOWN_WIDTHS:
                continue

            width_px = x2 - x1  # Bounding box width in pixels
            real_width = KNOWN_WIDTHS[label]  # Actual width in cm
            distance = (real_width * FOCAL_LENGTH) / width_px  # Distance estimation

            if label not in detected_objects:
                detected_objects[label] = []
            detected_objects[label].append(distance)

            # Draw bounding box and distance
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            distance_text = f"{label} {distance:.2f} cm"
            cv2.putText(frame, distance_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Compute average distances and trigger warnings
    if time.time() - last_update_time >= 5:
        for label, distances in detected_objects.items():
            avg_distance = np.mean(distances)
            distance_results[label] = avg_distance
            if avg_distance < CRITICAL_DISTANCE:
                warning_msg = f"Warning! {label} is too close: {avg_distance:.2f} cm"
                warnings.append(warning_msg)
        last_update_time = time.time()

    # Announce warnings
    for warning in warnings:
        print(warning)
        engine.say(warning)
        engine.runAndWait()

    cv2.imshow("YOLOv8 Distance Estimation", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
