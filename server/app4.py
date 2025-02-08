from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import cv2
import numpy as np
import base64

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load YOLO
net = cv2.dnn.readNet("C:\Rohit\Projects\SixthSense\model\yolov3.weights", "C:\Rohit\Projects\SixthSense\model\yolov3.cfg")
with open("C:\Rohit\Projects\SixthSense\model\coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

def decode_image(image_data):
    try:
        # Debug print to check incoming data
        print(f"Received image data length: {len(image_data)}")
        
        # Remove any whitespace and newlines
        image_data = image_data.strip()
        
        # Remove the data URL prefix if present
        if 'data:image/jpeg;base64,' in image_data:
            image_data = image_data.split('data:image/jpeg;base64,')[1]
            print("Removed data URL prefix")
        
        # Remove any additional whitespace after splitting
        image_data = image_data.strip()
        
        # Add padding if needed
        missing_padding = len(image_data) % 4
        if missing_padding:
            image_data += '=' * (4 - missing_padding)
            print(f"Added {4 - missing_padding} padding characters")
        
        # Decode base64 string to bytes
        try:
            image_bytes = base64.b64decode(image_data)
            print(f"Successfully decoded base64, bytes length: {len(image_bytes)}")
        except Exception as e:
            print(f"Base64 decoding failed: {str(e)}")
            raise
        
        # Convert bytes to numpy array
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            print(f"Converted to numpy array, shape: {nparr.shape}")
        except Exception as e:
            print(f"Numpy conversion failed: {str(e)}")
            raise
        
        # Decode image
        try:
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is not None:
                print(f"Successfully decoded image, shape: {image.shape}")
            else:
                print("cv2.imdecode returned None")
                raise ValueError("Failed to decode image")
        except Exception as e:
            print(f"OpenCV decoding failed: {str(e)}")
            raise
            
        return image
    except Exception as e:
        print(f"Error in decode_image: {str(e)}")
        return None
    
def detect_objects(image):
    height, width, _ = image.shape
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    
    net.setInput(blob)
    outs = net.forward(output_layers)
    
    detected_objects = []
    confidences = []
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence > 0.5:
                detected_objects.append(classes[class_id])
                confidences.append(float(confidence))
    
    return detected_objects, confidences

@socketio.on('send_frame')
def handle_frame(data):
    try:
        # Check if we received data
        if not data:
            print("No data received")
            return socketio.emit('detection_response', {
                'success': False,
                'error': 'No data received'
            })
        
        # Get image data
        image_data = data.get('image')
        if not image_data:
            print("No image data in payload")
            return socketio.emit('detection_response', {
                'success': False,
                'error': 'No image data in payload'
            })
        
        # Decode the image
        print("Attempting to decode image...")
        image = decode_image(image_data)
        if image is None:
            return socketio.emit('detection_response', {
                'success': False,
                'error': 'Failed to decode image'
            })
        
        # Detect objects
        print("Detecting objects...")
        objects, confidences = detect_objects(image)
        
        # Send response back to client
        print(f"Detection successful. Found {len(objects)} objects")
        socketio.emit('detection_response', {
            'success': True,
            'objects': objects,
            'confidences': confidences
        })
        
    except Exception as e:
        print(f"Error in handle_frame: {str(e)}")
        socketio.emit('detection_response', {
            'success': False,
            'error': str(e)
        })
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)