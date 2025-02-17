#!/usr/bin/env python3

import cv2
import mediapipe as mp
from signalflow import *

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def main():
    graph = AudioGraph()

    # Initialize Hands model in LIVE_STREAM mode
    with mp_hands.Hands(static_image_mode=False,
                        max_num_hands=8,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

        # Open webcam
        cap = cv2.VideoCapture(0)
        buffer = Buffer("../../audio/Molasses Pad v2-enhanced-v1.wav")
        buffer = Buffer("../../audio/Spectral Shimmer - Organs.wav")
        granulator_left = Granulator(buffer, clock=RandomImpulse(50), pos=0)
        granulator_left.play()
        granulator_right = Granulator(buffer, clock=RandomImpulse(50), pos=0)
        granulator_right.play()


        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame so that it appears in the natural mirror orientation
            frame = cv2.flip(frame, 1)

            # Convert frame to RGB (MediaPipe requires RGB input)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame to detect hands
            results = hands.process(frame_rgb)

            # If hands are detected, process landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                      results.multi_handedness):
                    # Draw landmarks on the frame
                    mp_drawing.draw_landmarks(frame,
                                              hand_landmarks,
                                              mp_hands.HAND_CONNECTIONS)
                
                    finger_tip_pos = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    if handedness.classification[0].label == "Left":
                        granulator_left.pos = finger_tip_pos.x * buffer.duration
                        granulator_left.clock.frequency = (1 - finger_tip_pos.y) * 100
                        granulator_left.duration = finger_tip_pos.y * 0.2
                    elif handedness.classification[0].label == "Right":                        
                        granulator_right.pos = finger_tip_pos.x * buffer.duration
                        granulator_right.clock.frequency = (1 - finger_tip_pos.y) * 100
                        granulator_right.duration = finger_tip_pos.y * 0.2

            height, width, _ = frame.shape

            import numpy as np
            y0 = 0
            for x in list(np.linspace(0, 1, 1024)):
                y1 = buffer.get(0, x * buffer.num_frames)  
                cv2.line(frame,
                         (int(x * width), int(height / 2 + y0 * 200)),
                         (int((x + 1/1024) * width), int(height / 2 + y1 * 200)),
                         (0, 0, 255),
                         1)
                y0 = y1
            
            # Display the frame
            cv2.imshow("Hand tracker", frame)

            # Exit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
