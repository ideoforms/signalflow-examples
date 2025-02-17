#!/usr/bin/env python3

# --------------------------------------------------------------------------------
# SignalFlow: Computer keyboard piano example
# Captures keyboard events to play the computer keyboard like a piano.
#
# Rows q-p and z-m correspond to white keys, with black keys above them.
# --------------------------------------------------------------------------------

from signalflow import *
from pynput import keyboard
import time
import glob
import random

def main():
    graph = AudioGraph()

    class SamplePlayer (Patch):
        def __init__(self, buffer):
            super().__init__()
            player = BufferPlayer(buffer, loop=False)
            self.set_output(player)
            self.set_auto_free(True)

    audio_root = "/Users/daniel/Projects/SignalFlow/Code/signalflow/notebooks/timbre-tools/audio/200-drum-machines"
    audio_files = glob.glob(f"{audio_root}/*.wav")
    buffers = {}
    for char_code in range(ord('a'), ord('z') + 1):
        char = chr(char_code)
        audio_file = random.choice(audio_files)
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

    print("Listening for notes...")
    print("Press [esc] to exit")

    running = True
    while running:
        time.sleep(0.1)


if __name__ == "__main__":
    main()