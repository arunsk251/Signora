import cv2
import mediapipe as mp
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import base64
import numpy as np

app = Flask(__name__)
CORS(app)

# Load model and encoder
model = joblib.load('asl_model.pkl')
encoder = joblib.load('label_encoder.pkl')

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.3)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    image_64 = data['image']

    # Decode base64 image
    image_data = base64.b64decode(image_64)
    np_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Process image with MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if not results.multi_hand_landmarks:
        return jsonify({'error': 'No hand detected'})

    # Extract landmarks
    landmark_list = []
    for lm in results.multi_hand_landmarks[0].landmark:
        landmark_list.extend([lm.x, lm.y, lm.z])

    # Predict
    y_pred = model.predict([landmark_list])
    prediction = encoder.inverse_transform(y_pred)[0]

    return jsonify({'prediction': prediction})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500, debug=True)
