#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# SignalFlow: Computer keyboard piano example
# Captures keyboard events to play the computer keyboard like a piano.
#
# Rows q-p and z-m correspond to white keys, with black keys above them.
#--------------------------------------------------------------------------------

from signalflow import *
from pynput import keyboard
import time

def main():
    graph = AudioGraph()
    voices = [None] * 128

    key_to_note = {
        'z': 0,
        's': 1,
        'x': 2,
        'd': 3,
        'c': 4,
        'v': 5,
        'g': 6,
        'b': 7,
        'h': 8,
        'n': 9,
        'j': 10,
        'm': 11,

        'q': 12,
        '2': 13,
        'w': 14,
        '3': 15,
        'e': 16,
        'r': 17,
        '5': 18,
        't': 19,
        '6': 20,
        'y': 21,
        '7': 22,
        'u': 23,

        'i': 24,
        '9': 25,
        'o': 26,
        '0': 27,
        'p': 28
    }

    class SineVoice (Patch):
        def __init__(self, frequency: float = 440, gate: float = 1):
            super().__init__()
            frequency = self.add_input("frequency", frequency)
            frequency = frequency * random_uniform(0.99, 1.01)
            sine = Tanh(SineOscillator(frequency) * 1.25)
            gate = self.add_input("gate", gate)
            env = ADSREnvelope(0.01, 0.1, 0.5, 2.0, gate=gate)
            output = sine * env * 0.25
            self.set_output(output)
            self.set_auto_free_node(env)

    def on_press(key):
        try:
            note = key_to_note[key.char] + 48
            if voices[note] is None:
                voices[note] = SineVoice(frequency=midi_note_to_frequency(note))
                voices[note].play()
        except AttributeError:
            if key == keyboard.Key.esc:
                global running
                print("Exiting...")
                running = False
        except KeyError:
            pass

    def on_release(key):
        try:
            note = key_to_note[key.char] + 48
            if voices[note] is not None:
                voices[note].set_input("gate", 0)
                voices[note] = None

        except AttributeError:
            pass
        except KeyError:
            pass


    listener = keyboard.Listener(on_press=on_press,
                                on_release=on_release,
                                suppress=True)
    listener.start()

    print("Listening for notes...")
    print("Press [esc] to exit")

    running = True
    while running:
        time.sleep(0.1)

if __name__ == "__main__":
    main()