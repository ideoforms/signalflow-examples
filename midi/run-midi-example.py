#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# SignalFlow: MIDI control example
# Requires a controller configured to send CC messages 1..8
#--------------------------------------------------------------------------------

from signalflow import *
from signalflow_midi import *
import argparse
import os


class BreakCutter (Patch):
    def __init__(self, buffer_path):
        super().__init__()
        buffer = Buffer(buffer_path)
        cutter = BeatCutter(buffer=buffer,
                            # TODO: segment_count select between 2, 4, 8, 16, 32
                            segment_count=8,
                            stutter_probability=MIDIControl(0, 0, 1, initial=0.0),
                            stutter_count=MIDIControl(1, 1, 32, curve="exponential", initial=2),
                            jump_probability=MIDIControl(2, 0, 1, initial=0),
                            duty_cycle=MIDIControl(3, 0, 1, initial=1.0),
                            segment_rate=MIDIControl(4, 0.25, 4, curve="exponential"))
        
        # TODO: What is a better curve for resonance?
        resonance = resonance=MIDIControl(10, 0.0, 0.99, curve="linear")
        filter = SVFilter(cutter,"low_pass",
                          cutoff=MIDIControl(8, 40, 10000, initial=10000, curve="exponential"),
                          resonance=resonance)
        filter = SVFilter(filter,
                          "high_pass",
                          cutoff=MIDIControl(9, 40, 20000, initial=40, curve="exponential"),
                          resonance=resonance)

        self.set_output(filter)


def main(args):
    graph = AudioGraph()

    #--------------------------------------------------------------------------------
    # To specify a specific MIDI input device, uncomment the line below.
    #
    # To list available MIDI input devices, use the signalflow command-line tool:
    #
    #     signalflow list-midi-input-device-names
    #--------------------------------------------------------------------------------
    os.environ["SIGNALFLOW_MIDI_OUTPUT_DEVICE_NAME"] = "SHIK N32B"

    breakcutter = BreakCutter("../audio/amen-brother.wav")
    breakcutter.play()

    graph.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)
