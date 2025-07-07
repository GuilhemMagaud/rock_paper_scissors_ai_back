import csv
import os
from flask import Flask, jsonify
from flask_cors import CORS
from model import KeyPointClassifier
import cv2 as cv
import mediapipe as mp
import tempfile

class Person:
    def __init__(self, sign="unknown"):
        self.sign = sign

playerA = Person()
playerB = Person()

def load_labels(path):
    with open(path, encoding='utf-8-sig') as f:
        return [row[0] for row in csv.reader(f)]

def predict_signs_from_image(image_path):
    image = cv.imread(image_path)
    if image is None:
        raise ValueError("Image not found or invalid image path.")
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.7)
    keypoint_classifier = KeyPointClassifier()
    keypoint_classifier_labels = load_labels('model/keypoint_classifier/keypoint_classifier_label.csv')
    image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    signs = []
    if results.multi_hand_landmarks is not None:
        for hand_landmarks in results.multi_hand_landmarks:
            image_width, image_height = image.shape[1], image.shape[0]
            landmark_list = []
            for landmark in hand_landmarks.landmark:
                x = min(int(landmark.x * image_width), image_width - 1)
                y = min(int(landmark.y * image_height), image_height - 1)
                landmark_list.append([x, y])
            base_x, base_y = landmark_list[0]
            rel_landmarks = [[x - base_x, y - base_y] for x, y in landmark_list]
            flat_landmarks = [coord for point in rel_landmarks for coord in point]
            max_value = max(map(abs, flat_landmarks)) or 1
            norm_landmarks = [n / max_value for n in flat_landmarks]
            hand_sign_id = keypoint_classifier(norm_landmarks)
            hand_sign_letter = keypoint_classifier_labels[hand_sign_id]
            signs.append(hand_sign_letter)
    else:
        signs = ["unknown", "unknown"]
    while len(signs) < 2:
        signs.append("unknown")
    return {"hand_sign_player1": signs[0], "hand_sign_player2": signs[1]}

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    return response
    
from flask import request

@app.route('/predict', methods=['POST'])
def predict():
    if 'frames' not in request.files:
        return jsonify({"error": "No frames provided"}), 400

    files = request.files.getlist('frames')
    results = []

    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)
            try:
                signs = predict_signs_from_image(temp_path)
                results.append(signs)
            except Exception as e:
                print(f"Error processing {file.filename}:", e)
                results.append({"hand_sign_player1": "error", "hand_sign_player2": "error"})

    return jsonify({"predictions": results}), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"ready": True}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))