#!/usr/bin/env python3

import cv2
import datetime
import mediapipe as mp
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import RunningMode
from mediapipe import Image

from signalflow import *


def main():
    graph = AudioGraph()

    class Whoosh (Patch):
        def __init__(self):
            super().__init__()
            cutoff = self.add_input("cutoff", 400)
            noise = WhiteNoise() * 0.5
            filter = SVFilter(noise, "low_pass", cutoff=Smooth(cutoff, 0.999), resonance=0.95)
            delay = CombDelay(filter, 0.2, feedback=0.7)
            filter_stereo = StereoPanner(filter + delay * 0.5)
            self.set_output(filter_stereo)

    whoosh = Whoosh()
    whoosh.play()

    samples = {
        "Thumb_Up": "ClopTone Eb3.wav",
        "Closed_Fist": "Chord Computer.wav",
    }

    players = {}
    for gesture_name, sample in samples.items():
        buffer = Buffer(f"../../audio/{sample}")
        player = BufferPlayer(buffer, clock=0)
        player.play()
        players[gesture_name] = player

    # Initialize MediaPipe Hands (for hand landmark tracking)
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    last_gesture = None

    # Callback function triggered when a gesture is recognized
    def gesture_callback(result, image, timestamp):
        nonlocal last_gesture
        if result.gestures:
            detected_gesture = result.gestures[0][0].category_name
            if detected_gesture != last_gesture:
                print(f"Gesture recognized: {detected_gesture}")
                if detected_gesture in players:
                    players[detected_gesture].trigger()
                last_gesture = detected_gesture

    # Load MediaPipe's Gesture Recognizer model with a callback
    options = GestureRecognizerOptions(base_options=BaseOptions(model_asset_path="model/gesture_recognizer.task"),
                                       running_mode=RunningMode.LIVE_STREAM,
                                       result_callback=gesture_callback)
    recognizer = GestureRecognizer.create_from_options(options)

    # Initialize Hands tracking
    with mp_hands.Hands(static_image_mode=False,
                        max_num_hands=2,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

        t0 = datetime.datetime.now()

        # Open webcam
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            # Convert frame to RGB (MediaPipe requires RGB input)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create an Image object for Gesture Recognizer
            mp_image = Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            # Recognize gestures asynchronously
            t1 = datetime.datetime.now()
            dt = int((t1 - t0).total_seconds() * 1000)
            recognizer.recognize_async(mp_image, timestamp_ms=dt)

            # Process hand landmarks using MediaPipe Hands
            results = hands.process(frame_rgb)

            # If hands are detected, draw landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                      results.multi_handedness):
                    mp_drawing.draw_landmarks(frame,
                                              hand_landmarks,
                                              mp_hands.HAND_CONNECTIONS)

                    if handedness.classification[0].label == "Right":
                        x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                        cutoff = scale_lin_exp(x, 0, 1, 40, 4000)
                        whoosh.set_input("cutoff", cutoff)

            # Display the frame
            cv2.imshow("Gesture Recognition + Hand Tracking", frame)

            # Exit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
