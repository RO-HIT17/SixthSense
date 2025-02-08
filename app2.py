import cv2
import numpy as np
import pyttsx3
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speaking speed

# Load YOLO Model
yolo_net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

# Define classes and real-world widths (in cm)
classes = [
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", 
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", 
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", 
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", 
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse", 
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]

KNOWN_WIDTHS = {
    "person": 40, "bicycle": 65, "car": 150, "motorbike": 70, "aeroplane": 500, "bus": 250, 
    "train": 300, "truck": 250, "boat": 200, "traffic light": 30, "fire hydrant": 50, 
    "stop sign": 60, "parking meter": 20, "bench": 120, "bird": 20, "cat": 30, "dog": 50, 
    "horse": 90, "sheep": 80, "cow": 150, "elephant": 300, "bear": 200, "zebra": 160, 
    "giraffe": 200, "backpack": 40, "umbrella": 90, "handbag": 30, "tie": 20, "suitcase": 60, 
    "frisbee": 30, "skis": 160, "snowboard": 160, "sports ball": 22, "kite": 150, 
    "baseball bat": 100, "baseball glove": 30, "skateboard": 80, "surfboard": 180, 
    "tennis racket": 70, "bottle": 10, "wine glass": 9, "cup": 10, "fork": 20, "knife": 20, 
    "spoon": 20, "bowl": 20, "banana": 20, "apple": 15, "sandwich": 15, "orange": 15, 
    "broccoli": 20, "carrot": 15, "hot dog": 20, "pizza": 30, "donut": 15, "cake": 30, 
    "chair": 100, "sofa": 200, "pottedplant": 50, "bed": 200, "diningtable": 180, 
    "toilet": 60, "tvmonitor": 100, "laptop": 40, "mouse": 10, "remote": 20, "keyboard": 45, 
    "cell phone": 15, "microwave": 50, "oven": 60, "toaster": 30, "sink": 60, "refrigerator": 150,
    "book": 30, "clock": 30, "vase": 30, "scissors": 20, "teddy bear": 40, "hair drier": 30, 
    "toothbrush": 20
}

# Focal length (calibrated for a Dell laptop webcam)
FOCAL_LENGTH = 500  # Approximate value, should be calibrated for accuracy

# Critical distance threshold for warnings (in cm)
CRITICAL_DISTANCE = 50  # Adjust as needed

# Start Webcam
cap = cv2.VideoCapture(0)
last_update_time = time.time()
distance_results = {}

while True:
    ret, frame = cap.read()
    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), swapRB=True, crop=False)
    yolo_net.setInput(blob)
    detections = yolo_net.forward(output_layers)

    detected_objects = {}
    warning_message = ""

    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                label = classes[class_id] if class_id < len(classes) else "unknown"
                if label not in KNOWN_WIDTHS:
                    continue

                center_x, center_y, w, h = (
                    int(obj[0] * width), int(obj[1] * height),
                    int(obj[2] * width), int(obj[3] * height)
                )
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                if label not in detected_objects:
                    detected_objects[label] = {"x": [], "y": [], "w": [], "h": [], "distances": []}

                detected_objects[label]["x"].append(x)
                detected_objects[label]["y"].append(y)
                detected_objects[label]["w"].append(w)
                detected_objects[label]["h"].append(h)

                if time.time() - last_update_time >= 5:
                    real_width = KNOWN_WIDTHS[label]
                    distance = (real_width * FOCAL_LENGTH) / w
                    detected_objects[label]["distances"].append(distance)

    if time.time() - last_update_time >= 10:
        for label, data in detected_objects.items():
            if data["distances"]:
                avg_distance = np.mean(data["distances"])
                distance_results[label] = avg_distance
                if avg_distance < CRITICAL_DISTANCE:
                    warning_message = f"Warning! {label} is too close: {avg_distance:.2f} cm"
        last_update_time = time.time()

    for label, data in detected_objects.items():
        avg_x = int(np.mean(data["x"]))
        avg_y = int(np.mean(data["y"]))
        avg_w = int(np.mean(data["w"]))
        avg_h = int(np.mean(data["h"]))

        cv2.rectangle(frame, (avg_x, avg_y), (avg_x + avg_w, avg_y + avg_h), (0, 255, 0), 2)
        distance_value = distance_results.get(label, None)
        distance_text = f"{label}: {distance_value:.2f} cm" if distance_value else f"{label}: Calculating..."
        cv2.putText(frame, distance_text, (avg_x, avg_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if warning_message:
        print(warning_message)
        engine.say(warning_message)
        engine.runAndWait()

    cv2.imshow("YOLO Object Detection with Distance Warning", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
