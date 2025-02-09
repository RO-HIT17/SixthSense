from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pyttsx3

app = Flask(__name__)
CORS(app)

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyDrsZPrN-5yZhz0v1yE73gg_vphwuXRZsM"

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def text_to_speech(text):
    """Convert text to speech and play it"""
    engine.say(text)
    engine.runAndWait()

@app.route("/get-directions", methods=["POST"])
def get_directions():
    try:
        data = request.get_json()
        origin = data.get("origin")  # Example: "New York"
        destination = data.get("destination")  # Example: "Los Angeles"

        if not origin or not destination:
            return jsonify({"error": "Missing origin or destination"}), 400

        # Get lat/lon for place names using Geocoding API
        geocode_origin = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={origin}&key={GOOGLE_MAPS_API_KEY}").json()
        geocode_destination = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={destination}&key={GOOGLE_MAPS_API_KEY}").json()

        if not geocode_origin["results"] or not geocode_destination["results"]:
            return jsonify({"error": "Invalid place name"}), 400

        origin_coords = geocode_origin["results"][0]["geometry"]["location"]
        destination_coords = geocode_destination["results"][0]["geometry"]["location"]

        origin_latlon = f"{origin_coords['lat']},{origin_coords['lng']}"
        destination_latlon = f"{destination_coords['lat']},{destination_coords['lng']}"

        # Get directions from Google Maps Directions API
        google_maps_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin_latlon}&destination={destination_latlon}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(google_maps_url)
        data = response.json()

        if "routes" not in data or len(data["routes"]) == 0:
            return jsonify({"error": "No route found"}), 404

        # Extract step-by-step navigation
        steps = []
        for step in data["routes"][0]["legs"][0]["steps"]:
            instruction = step["html_instructions"].replace("<b>", "").replace("</b>", "").replace("&nbsp;", " ")
            steps.append(instruction)

        # Convert text directions into speech
        full_instructions = ". ".join(steps)
        #text_to_speech(full_instructions)

        return jsonify({"directions": steps})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
