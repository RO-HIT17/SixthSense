from flask import Flask
from flask_socketio import SocketIO
import base64
import numpy as np
import cv2
import eventlet
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
print("Server started")

@socketio.on('send_frame')
def handle_frame(data):
    try:
        image_data = data.get("image")

        img_data = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        cv2.imshow("Received Frame", frame)
        cv2.waitKey(1)

        detected_objects = ["person", "car"]  

        socketio.emit("response", {"objects": detected_objects})
    
    except Exception as e:
        print("Error processing frame:", e)

if __name__ == "__main__":
    socketio.run(app, host="192.168.29.251", port=5000)
