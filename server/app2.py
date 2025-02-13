from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import time

app = Flask(__name__)
CORS(app)  


net = cv2.dnn.readNet("C:\Rohit\Projects\SixthSense\model\yolov3.weights", "C:\Rohit\Projects\SixthSense\model\yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
classes = open("C:\Rohit\Projects\SixthSense\model\coco.names").read().strip().split("\n")

@app.route("/detect", methods=["POST"])
def detect_objects():
    data = request.json
    image_data = data.get("image", "")

    if not image_data:
        return jsonify({"error": "No image received"})

    try:
        decoded = base64.b64decode(image_data)
        np_arr = np.frombuffer(decoded, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        height, width, channels = img.shape
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        detections = net.forward(output_layers)

        detected_objects = []
        for output in detections:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    detected_objects.append(classes[class_id])

        return jsonify({"objects": list(set(detected_objects))})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
