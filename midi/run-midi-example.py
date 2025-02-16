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
                            stutter_probability=MIDIControl(0, 0, 1),
                            stutter_count=MIDIControl(1, 1, 32, curve="exponential"),
                            jump_probability=MIDIControl(2, 0, 1),
                            duty_cycle=MIDIControl(3, 0, 1, initial=1.0),
                            segment_rate=MIDIControl(4, 0.25, 4, curve="exponential"))
        self.set_output(cutter)


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
