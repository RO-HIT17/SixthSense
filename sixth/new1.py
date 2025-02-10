from flask import Flask, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow requests from the phone

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    return f"File saved: {filepath}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
