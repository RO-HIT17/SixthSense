from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from gtts import gTTS
import os

app = Flask(__name__)
CORS(app)

# Load YOLO model
yolo_net = cv2.dnn.readNet("model\yolo.weights", "model\yolo.cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]
class_labels = open("model\coco.names").read().strip().split("\n")  # Load class names

# Function to process image using YOLO
def process_image(image):
    # Decode base64 to OpenCV format
    img_data = base64.b64decode(image)
    np_arr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Get image dimensions
    height, width, _ = frame.shape

    # Convert image to YOLO format
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    yolo_net.setInput(blob)
    outputs = yolo_net.forward(output_layers)

    detected_objects = []

    # Process YOLO outputs
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:  # Confidence threshold
                detected_objects.append(class_labels[class_id])

    return detected_objects

# API to receive image from mobile app
@app.route('/detect', methods=['POST'])
def detect_objects():
    data = request.get_json()
    image_data = data.get("image")

    if not image_data:
        return jsonify({"error": "No image provided"}), 400

    detected_objects = process_image(image_data)

    # Generate a voice alert if specific objects are detected
    alert_text = ""
    if "person" in detected_objects:
        alert_text = "Warning! Person detected."
        tts = gTTS(text=alert_text, lang='en')
        tts.save("alert.mp3")

    return jsonify({"objects": detected_objects, "alert": alert_text})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
