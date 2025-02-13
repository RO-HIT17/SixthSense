from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import base64
import os
import cv2
import numpy as np
import logging
import time
import pyttsx3  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

os.makedirs("uploads", exist_ok=True)

yolo_net = cv2.dnn.readNet("C:\Rohit\Projects\SixthSense\model\yolov3.weights", "C:\Rohit\Projects\SixthSense\model\yolov3.cfg")
with open("C:\Rohit\Projects\SixthSense\model\coco.names", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

tts_engine = pyttsx3.init()

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.json
        base64_image = data.get('image', '')
        return process_image(base64_image)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory('uploads', filename)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('send_frame')
def handle_frame(data):
    try:
        image_data = data.get('image', '')
        result = process_image(image_data)

        if result["success"]:
            socketio.emit('detection_response', {
                "success": True,
                "message": "Image processed successfully",
                "result": result
            })
        else:
            socketio.emit('detection_response', {
                "success": False,
                "error": result["error"]
            })
    except Exception as e:
        socketio.emit('detection_response', {
            "success": False,
            "error": str(e)
        })

def process_image(base64_image):
    if not base64_image:
        raise ValueError("No image data received")

    try:
        base64_string = base64_image.replace('data:image/jpeg;base64,', '')
        base64_string = base64_string.replace('data:image/png;base64,', '')
        base64_string = base64_string.replace(' ', '+')  
        
        base64_string = ''.join(c for c in base64_string if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        missing_padding = len(base64_string) % 4
        if missing_padding:
            base64_string += '=' * (4 - missing_padding)

        image_bytes = base64.b64decode(base64_string)
        image_np = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image")

        image_path = os.path.join("uploads", f"frame_{int(time.time())}.jpg")
        cv2.imwrite(image_path, img)

        detected_objects = detect_objects(img)

        audio_path = generate_audio(detected_objects)

        return {
            "success": True,
            "message": "Image processed successfully!",
            "objects": detected_objects,
            "audio_url": audio_path  
        }

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"success": False, "error": str(e)}

def detect_objects(img):
    height, width, channels = img.shape
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    yolo_net.setInput(blob)
    outputs = yolo_net.forward(output_layers)

    class_ids, confidences, boxes = [], [], []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                center_x, center_y, w, h = (detection[:4] * [width, height, width, height]).astype("int")
                x, y = int(center_x - w / 2), int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    detected_objects = []
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    if len(indexes) > 0:
        for i in indexes.flatten():
            label = class_names[class_ids[i]]
            detected_objects.append(label)

    return detected_objects

def generate_audio(detected_objects):
    if not detected_objects:
        text_response = "No objects detected."
    else:
        text_response = "Detected objects: " + ", ".join(detected_objects)

    logger.info(f"TTS Response: {text_response}")

    audio_filename = f"audio_{int(time.time())}.mp3"
    audio_file = os.path.join("uploads", audio_filename)
    tts_engine.save_to_file(text_response, audio_file)
    tts_engine.runAndWait()

    return f"/uploads/{audio_filename}"

if __name__ == '__main__':
    try:
        logger.info("Starting video server on http://0.0.0.0:5000")
        socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
    finally:
        cv2.destroyAllWindows()
