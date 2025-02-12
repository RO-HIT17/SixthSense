from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import requests
import googlemaps
from gtts import gTTS
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
from dotenv import load_dotenv

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

user_locations = {}
@app.route('/start-navigation', methods=['POST'])
def start_navigation():
    data = request.json
    source = data.get('source')
    destination = data.get('destination')

    if not source or not destination:
        return jsonify({"error": "Source and Destination are required"}), 400

    try:
        source_coords = gmaps.geocode(source)[0]['geometry']['location']
        dest_coords = gmaps.geocode(destination)[0]['geometry']['location']

        directions = gmaps.directions(source, destination, mode="driving")

        if not directions:
            return jsonify({"error": "No route found"}), 400

        steps = directions[0]['legs'][0]['steps']
        instructions = [
            {
                "distance": step['distance']['text'],
                "duration": step['duration']['text'],
                "instruction": step['html_instructions']
            }
            for step in steps
        ]

        text_to_speech(instructions[0]["instruction"])

        return jsonify({
            "source_coords": source_coords,
            "destination_coords": dest_coords,
            "instructions": instructions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/location_update', methods=['POST'])
def location_update():
    data = request.json
    user_id = data.get('user_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not user_id or not latitude or not longitude:
        return jsonify({"error": "Missing parameters"}), 400

    user_locations[user_id] = {"latitude": latitude, "longitude": longitude}

    socketio.emit('location_update', {
        "user_id": user_id,
        "latitude": latitude,
        "longitude": longitude
    })

    return jsonify({"message": "Location updated"})


def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("instruction.mp3")
        return "instruction.mp3"
    except Exception as e:
        print("Error generating speech:", e)
        return None


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
