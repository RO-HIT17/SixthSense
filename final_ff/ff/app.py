from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/transcription', methods=['POST'])
def receive_transcription():
    data = request.json
    text = data.get("transcription", "")

    if not text:
        return jsonify({"error": "No transcription received"}), 400

    print("Received Transcription:", text)
    return jsonify({"message": "Transcription received successfully", "text": text})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
