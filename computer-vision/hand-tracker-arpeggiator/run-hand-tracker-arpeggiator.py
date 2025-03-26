#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# SignalFlow: Hand tracker example
# Sends MIDI triggers to the default MIDI device.
#--------------------------------------------------------------------------------

import cv2
import mediapipe as mp
import numpy as np
from signalflow import *
from isobar import *

def map_x_to_note(x):
    x_note = int(scale_lin_lin(x, 0, 1, 16, 44))
    return x_note

def main():
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    full_screen = False

    timeline = Timeline(150)
    timeline.start()

    sequence = PSequence([None, None, None, None, None])
    track = timeline.schedule({
        "degree": sequence,
        "key": Key("C", "minorPenta"),
        "duration": PSequence([0.25, 0.25, 0.25, 0.25, 0.5]),
    }, quantize=1)

    # Initialize Hands model in LIVE_STREAM mode
    with mp_hands.Hands(static_image_mode=False,
                        max_num_hands=8,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

        # Open webcam
        cap = cv2.VideoCapture(0)
        if full_screen:
            cv2.namedWindow("handtracker", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("handtracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame so that it appears in the natural mirror orientation
            frame = cv2.flip(frame, 1)
            empty = np.zeros(frame.shape)

            # Convert frame to RGB (MediaPipe requires RGB input)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame to detect hands
            results = hands.process(frame_rgb)

            # If hands are detected, process landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                      results.multi_handedness):
                    # Draw landmarks on the frame
                    mp_drawing.draw_landmarks(empty,
                                              hand_landmarks,
                                              mp_hands.HAND_CONNECTIONS)
                    
                    if handedness.classification[0].label == "Right":
                        finger_0_pos = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                        sequence.sequence[0] = map_x_to_note(finger_0_pos.x)

                        finger_1_pos = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        sequence.sequence[1] = map_x_to_note(finger_1_pos.x)
                        
                        finger_2_pos = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                        sequence.sequence[2] = map_x_to_note(finger_2_pos.x)

                        finger_3_pos = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                        sequence.sequence[3] = map_x_to_note(finger_3_pos.x)

                        finger_4_pos = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                        sequence.sequence[4] = map_x_to_note(finger_4_pos.x)
                    else:
                        finger_0_pos = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        transpose = int(scale_lin_lin(finger_0_pos.y, 1, 0, -3, 3)) * 2
                        track.transpose = transpose
                        
            
            # Display the frame
            cv2.imshow("handtracker", empty)

            # Exit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
