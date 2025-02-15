#!/usr/bin/env python3

import cv2
import datetime
import mediapipe as mp
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import RunningMode
from mediapipe import Image


def main():
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
                print(f"Gesture Recognized: {detected_gesture}")
                last_gesture = detected_gesture

    # Load MediaPipe's Gesture Recognizer model with a callback
    options = GestureRecognizerOptions(base_options=BaseOptions(model_asset_path="model/gesture_recognizer.task"),
                                       running_mode=RunningMode.LIVE_STREAM,
                                       result_callback=gesture_callback)
    recognizer = GestureRecognizer.create_from_options(options)

    # Open webcam
    cap = cv2.VideoCapture(0)

    # Initialize Hands tracking
    with mp_hands.Hands(static_image_mode=False,
                        max_num_hands=2,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

        t0 = datetime.datetime.now()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

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
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame,
                                              hand_landmarks,
                                              mp_hands.HAND_CONNECTIONS)

                    # Optionally: Draw hand landmarks on the image
                    for landmark in hand_landmarks.landmark:
                        h, w, c = frame.shape
                        cx, cy = int(landmark.x * w), int(landmark.y * h)
                        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

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
