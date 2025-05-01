from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)               # ← enable CORS for all routes

last_mood = None

@app.route('/set_mood', methods=['POST'])
def set_mood():
    global last_mood
    data = request.get_json()
    mood = data.get('mood')
    if not mood:
        return jsonify({"error": "No mood provided"}), 400
    last_mood = mood
    return jsonify({"status": "success", "lastMood": last_mood}), 200

@app.route('/get_mood', methods=['GET'])
def get_mood():
    return jsonify({"lastMood": last_mood}), 200

if __name__ == '__main__':
    app.run(port=5000)
