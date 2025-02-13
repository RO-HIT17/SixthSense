from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import numpy as np
import base64
import eventlet
import io

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_frame(data):
    image_data = data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    _, buffer = cv2.imencode('.jpg', processed_frame)
    processed_base64 = base64.b64encode(buffer).decode("utf-8")
    socketio.send(f"data:image/jpeg;base64,{processed_base64}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
