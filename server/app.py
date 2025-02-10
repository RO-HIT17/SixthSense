from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import base64
import os
import cv2
import numpy as np
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

os.makedirs("uploads", exist_ok=True)

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
        socketio.emit('detection_response', {
            "success": True,
            "message": "Image processed successfully",
            "result": result
        })
    except Exception as e:
        print("Error processing frame:", str(e))
        socketio.emit('detection_response', {
            "success": False,
            "error": str(e)
        })

def process_image(base64_image):
    if not base64_image:
        raise ValueError("No image data received")

    try:
        base64_image = base64_image.split(",")[-1]  # Remove any metadata
        base64_image = base64_image.replace(" ", "+")  # Fix spaces
        missing_padding = len(base64_image) % 4
        if missing_padding:
            base64_image += "=" * (4 - missing_padding)

        image_bytes = base64.b64decode(base64_image)
        image_np = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image")

        image_path = os.path.join("uploads", f"frame_{int(time.time())}.jpg")
        cv2.imwrite(image_path, img)

        return {
            "success": True,
            "message": "Image processed successfully!",
            "path": image_path
        }

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    logger.info("Starting server on http://0.0.0.0:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
