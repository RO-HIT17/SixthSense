import cv2
import numpy as np
import av
from flask import Flask, render_template
from flask_socketio import SocketIO
from aiortc import RTCPeerConnection, VideoStreamTrack
from aiortc.contrib.media import MediaRelay

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

pc = RTCPeerConnection()
relay = MediaRelay()

@app.route("/")
def index():
    return render_template("index.html")  # Loads frontend WebRTC page

class VideoTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()
        self.track = relay.subscribe(track)
    
    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        obstacles = cv2.Canny(gray, 50, 150)  # Example edge detection

        # Convert back to BGR
        img[obstacles > 0] = [0, 255, 0]  # Highlight obstacles in green

        # Encode back to video frame
        new_frame = av.VideoFrame.from_ndarray(img, format="bgr24")
        return new_frame

@socketio.on("offer")
async def handle_offer(data):
    offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
    await pc.setRemoteDescription(offer)
    
    # Process video stream
    for track in pc.getReceivers():
        if track.kind == "video":
            pc.addTrack(VideoTrack(track))

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    socketio.emit("answer", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
