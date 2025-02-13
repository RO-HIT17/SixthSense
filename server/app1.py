from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
from gtts import gTTS
import os

app = Flask(__name__)
CORS(app)

yolo_net = cv2.dnn.readNet("C:\Rohit\Projects\SixthSense\model\yolov3.weights", "C:\Rohit\Projects\SixthSense\model\yolov3.cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]
class_labels = open("C:\Rohit\Projects\SixthSense\model\coco.names").read().strip().split("\n")

def process_image(image):
    img_data = base64.b64decode(image)
    np_arr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    yolo_net.setInput(blob)
    outputs = yolo_net.forward(output_layers)

    detected_objects = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                detected_objects.append(class_labels[class_id])

    return detected_objects

@app.route('/detect', methods=['POST'])
def detect_objects():
    data = request.get_json()
    image_data = data.get("image")
    if not image_data:
        return jsonify({"error": "No image provided"}), 400

    detected_objects = process_image(image_data)

    alert_text = ""
    if "person" in detected_objects:
        alert_text = "Warning! Person detected."
        tts = gTTS(text=alert_text, lang='en')
        tts.save("alert.mp3")

    return jsonify({"objects": detected_objects, "alert": alert_text})

@app.route('/alert.mp3', methods=['GET'])
def get_audio():
    return send_file("alert.mp3", mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
