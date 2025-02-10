from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/text', methods=['GET'])
def get_text():
    return jsonify({"message": "Hello! Welcome to our app. How can I assist you today?"})

@app.route('/api/speech', methods=['POST'])
def receive_speech_text():
    data = request.json
    spoken_text = data.get("text", "")
    #Rohit will work here to convert the spoken_text to ml code
    print(f"Received Speech Text: {spoken_text}")
    return jsonify({"response": f"Received: {spoken_text}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
