from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import numpy as np
import base64
import pyttsx3
import io

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

tts = pyttsx3.init()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def process_frame(data):
    image_data = data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    if np.sum(edges) > 500000:  
        feedback_text = "Obstacle ahead! Please be careful."
    else:
        feedback_text = ""

    if feedback_text:
        tts.save_to_file(feedback_text, "static/audio_feedback.mp3")
        tts.runAndWait()
        socketio.send("http://192.168.1.5:5000/static/audio_feedback.mp3")  

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
