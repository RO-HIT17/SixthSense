import cv2
import numpy as np

# Load YOLO Model
yolo_net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i-1] for i in yolo_net.getUnconnectedOutLayers()]

# Define classes (use the classes from your dataset)
classes = ["person", "car", "dog", "bicycle", "cell phone","bottle"]  

# Focal Length (calibrated for your camera)
FOCAL_LENGTH = 500  # Change based on your calibration

# Define real-world object widths (in cm) for objects you want to measure
KNOWN_WIDTHS = {
    "person": 40,  # Approximate shoulder width of a person
    "car": 150,    # Approximate car width
    "dog": 50,     # Approximate dog width
    "bicycle": 65,
    "cell phone":15,
    "bottle":15# Approximate bicycle width
}

# Start Webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    height, width, channels = frame.shape

    # Convert image to YOLO format
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), swapRB=True, crop=False)
    yolo_net.setInput(blob)
    detections = yolo_net.forward(output_layers)

    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                # Get bounding box dimensions
                center_x, center_y, w, h = (
                    int(obj[0] * width),
                    int(obj[1] * height),
                    int(obj[2] * width),
                    int(obj[3] * height),
                )
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # Distance Calculation
                label = classes[class_id]
                if label in KNOWN_WIDTHS:
                    real_width = KNOWN_WIDTHS[label]
                    distance = (real_width * FOCAL_LENGTH) / w  # w = detected width in pixels
                    distance_text = f"{label}: {distance:.2f} cm"
                else:
                    distance_text = f"{label}: Unknown distance"

                # Draw bounding box and display distance
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, distance_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("YOLO Object Detection with Distance Measurement", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
