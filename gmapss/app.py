from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import requests
import googlemaps
from gtts import gTTS
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

GOOGLE_MAPS_API_KEY = "AIzaSyDrsZPrN-5yZhz0v1yE73gg_vphwuXRZsM"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Store navigation data for each user
active_sessions = {}

@app.route("/start-navigation", methods=["POST"])
def start_navigation():
    """Fetches navigation waypoints and sends initial instructions"""
    data = request.json
    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return jsonify({"error": "Missing origin or destination"}), 400

    # Fetch directions from Google Maps API
    directions = gmaps.directions(origin, destination, mode="walking")

    if not directions:
        return jsonify({"error": "Could not fetch directions"}), 500

    steps = directions[0]['legs'][0]['steps']
    waypoints = []

    for step in steps:
        location = step['start_location']
        instruction = step['html_instructions']
        waypoints.append({
            "lat": location['lat'],
            "lng": location['lng'],
            "instruction": instruction
        })

    session_id = origin + "-" + destination  # Unique session ID
    active_sessions[session_id] = waypoints

    return jsonify({"session_id": session_id, "waypoints": waypoints})


@socketio.on("location_update")
def handle_location_update(data):
    """Listens for live user location updates & sends next instruction"""
    session_id = data.get("session_id")
    user_lat = data.get("lat")
    user_lng = data.get("lng")

    if session_id not in active_sessions:
        return

    waypoints = active_sessions[session_id]
    
    for index, waypoint in enumerate(waypoints):
        lat, lng, instruction = waypoint["lat"], waypoint["lng"], waypoint["instruction"]

        # Check if the user is near the next waypoint
        if abs(user_lat - lat) < 0.0005 and abs(user_lng - lng) < 0.0005:
            socketio.emit("navigation_instruction", {"instruction": instruction})

            # Convert instruction to voice
            tts = gTTS(text=instruction, lang="en")
            tts.save("instruction.mp3")
            os.system("mpg321 instruction.mp3")  # Play audio
            
            # Remove the waypoint after reaching
            active_sessions[session_id] = waypoints[index+1:]
            break


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
