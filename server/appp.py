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

# Create an "uploads" directory to store received images
os.makedirs("uploads", exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.json
        base64_image = data.get('image', '')
        return process_image(base64_image)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        # Clean up the base64 string
        base64_string = base64_image.replace('data:image/jpeg;base64,', '')
        base64_string = base64_string.replace('data:image/png;base64,', '')
        base64_string = base64_string.replace(' ', '+')  # Fix potential space issues
        
        # Remove any non-base64 characters
        base64_string = ''.join(c for c in base64_string if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        
        logger.info(f"Base64 string length: {len(base64_string)}")
        
        # Add padding if necessary
        missing_padding = len(base64_string) % 4
        if missing_padding:
            base64_string += '=' * (4 - missing_padding)

        try:
            # First attempt: direct decode
            image_bytes = base64.b64decode(base64_string)
        except Exception as e:
            logger.warning(f"First decode attempt failed: {e}")
            # Second attempt: with strict validation off
            image_bytes = base64.b64decode(base64_string + '==', validate=False)

        image_np = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image after successful base64 decode")

        # Show the image dimensions for debugging
        logger.info(f"Decoded image shape: {img.shape}")

        # Save and display image
        image_path = os.path.join("uploads", f"frame_{int(time.time())}.jpg")
        cv2.imwrite(image_path, img)
        cv2.imshow("Received Frame", img)
        cv2.waitKey(1)

        return {
            "success": True,
            "message": "Image processed successfully!",
            "path": image_path
        }

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        logger.error(f"Base64 string prefix: {base64_image[:50]}...")  # Show start of string for debugging
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    try:
        logger.info("Starting video server on http://0.0.0.0:5000")
        socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
    finally:
        cv2.destroyAllWindows()