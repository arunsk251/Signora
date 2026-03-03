import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pickle
import numpy as np
import cv2

st.set_page_config(page_title="Signora Live: Two-Hand Mode", page_icon="🤟")

# 1. Load the Random Forest model
@st.cache_resource
def load_rf_model():
    with open('sign_lang_rf_tasks.pkl', 'rb') as f:
        return pickle.load(f)

# 2. Setup the MediaPipe Landmarker for 2 hands
@st.cache_resource
def load_hand_detector():
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2, # Now correctly set for two-hand detection
        min_hand_detection_confidence=0.5
    )
    return vision.HandLandmarker.create_from_options(options)

model = load_rf_model()
detector = load_hand_detector()

class GestureTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Convert to MediaPipe Image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        detection_result = detector.detect(mp_image)
        
        # If any hands are detected
        if detection_result.hand_landmarks:
            # Iterate through all detected hands (up to 2)
            for i, hand_landmarks in enumerate(detection_result.hand_landmarks):
                # Extract 63 coordinates for THIS specific hand
                coords = []
                for lm in hand_landmarks:
                    coords.extend([lm.x, lm.y, lm.z])
                
                # Predict the gesture for this hand
                # Ensure the input is 2D: [ [x1, y1, z1, ...] ]
                prediction = model.predict([coords])
                gesture_name = prediction[0]
                
                # Visual Feedback: Draw landmarks for this hand
                self.draw_landmarks(img, hand_landmarks)
                
                # Overlay text: Each hand gets its own line
                y_pos = 50 + (i * 40) # Offset vertically so labels don't overlap
                display_text = f"Hand {i+1}: {gesture_name}"
                cv2.putText(img, display_text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 255, 0), 2, cv2.LINE_AA)
        else:
            cv2.putText(img, "No Hand Detected", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 0, 255), 2, cv2.LINE_AA)
        
        return img

    def draw_landmarks(self, img, landmarks):
        h, w, _ = img.shape
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), -1)

def main():
    st.title("Gesture")

    webrtc_streamer(
        key="sign-lang-live",
        video_processor_factory=GestureTransformer,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        }
    )

if __name__ == "__main__":
    main()