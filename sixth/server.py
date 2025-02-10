from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import azure.cognitiveservices.speech as speechsdk

app = Flask(__name__)
CORS(app)

AZURE_SPEECH_KEY = "3nF1650hHykjRygiBdmSgJQ8U08bOXEmgGXz8qIFlbya8Wa3UUDzJQQJ99BBACYeBjFXJ3w3AAAYACOGIx0Z"
AZURE_SPEECH_REGION = "eastus"

def convert_speech_to_text(audio_path):
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)

    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    result = recognizer.recognize_once()

    return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else "Speech not recognized"

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    audio_file = request.files["audio"]
    audio_path = f"./uploads/{audio_file.filename}"
    
    os.makedirs("./uploads", exist_ok=True)
    audio_file.save(audio_path)

    transcription = convert_speech_to_text(audio_path)
    return jsonify({"transcription": transcription})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
