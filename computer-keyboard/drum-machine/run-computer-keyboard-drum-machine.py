#!/usr/bin/env python3

# --------------------------------------------------------------------------------
# SignalFlow: Computer keyboard drum machine example
# Captures keyboard events to trigger samples
# --------------------------------------------------------------------------------

from signalflow import *
from pynput import keyboard
import time
import glob
import argparse

def main(audio_root):
    graph = AudioGraph()

    class SamplePlayer (Patch):
        def __init__(self, buffer):
            super().__init__()
            player = BufferPlayer(buffer, loop=False)
            if buffer.num_channels == 1:
                player = StereoPanner(player)
            
            self.set_output(player)
            self.set_auto_free(True)

    audio_files = glob.glob(f"{audio_root}/*.wav")
    buffers = {}
    for char_code in range(ord('a'), ord('z') + 1):
        char = chr(char_code)
        drum_index = char_code - ord('a')
        audio_file = audio_files[drum_index % len(audio_files)]
        buffers[char] = Buffer(audio_file)

    def on_press(key):
        try:
            char = key.char
            if char in buffers:
                buffer = buffers[char]
                player = SamplePlayer(buffer)
                player.play()
        except:
            if key == keyboard.Key.esc:
                nonlocal running
                running = False


    listener = keyboard.Listener(on_press=on_press,
                                 suppress=True)
    listener.start()

    print("Listening for trigger events on keys 'a' to 'z'...")
    print("Press [esc] to exit")

    running = True
    while running:
        time.sleep(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the computer keyboard drum machine.")
    parser.add_argument("audio_root", type=str, help="Path to the directory containing audio files.")
    args = parser.parse_args()

    main(args.audio_root)