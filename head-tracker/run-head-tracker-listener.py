#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# SignalFlow: Head tracker example
# Designed for the Supperware Head Tracker 1:
# https://supperware.co.uk/headtracker-overview
#
#
# Run Bridgehead, and set Profile to Yaw/Pitch/Roll (learnable)
#--------------------------------------------------------------------------------

from signalflow import *
import argparse

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

class BreakPlayer (Patch):
    def __init__(self, buffer_path):
        super().__init__()
        cutoff = self.add_input("cutoff", 440)
        delay = self.add_input("delay", 0.25)
        delay_time = self.add_input("delay_time", 0.2)
        buffer = Buffer(buffer_path)
        player = BufferPlayer(buffer, loop=True) * 0.5
        filter = SVFilter(player, "low_pass", cutoff=cutoff, resonance=0.9)
        delayed = CombDelay(filter, delay_time, feedback=0.9)
        output = filter + delayed * delay
        self.set_output(output)

def main(args):
    graph = AudioGraph()

    break_player = BreakPlayer("../audio/amen-brother.wav")
    break_player.play()

    def yaw_handler(_, yaw):
        print("yaw: %s" % yaw)
        break_player.set_input("delay_time", scale_lin_lin(yaw, 0, 1, 0.01, 0.3))
    def pitch_handler(_, pitch):
        print("pitch: %s" % pitch)
        cutoff = scale_lin_lin(pitch, 0, 1, 5, 10000)
        break_player.set_input("cutoff", cutoff)
    def roll_handler(_, roll):
        print("roll: %s" % roll)
        break_player.set_input("delay", roll)

    dispatcher = Dispatcher()
    dispatcher.map("/yaw", yaw_handler)
    dispatcher.map("/pitch", pitch_handler)
    dispatcher.map("/roll", roll_handler)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Listening for OSC on {}".format(server.server_address))
    print("Please connect a Supperware head tracker and start the Bridgehead software in Yaw/Pitch/Roll mode")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(args)
