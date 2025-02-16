#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# Head tracker example
# Designed for the Supperware Head Tracker 1:
# https://supperware.co.uk/headtracker-overview
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
        buffer = Buffer(buffer_path)
        player = BufferPlayer(buffer, loop=True)
        filter = SVFilter(player, "low_pass", cutoff=cutoff, resonance=0.9)
        self.set_output(filter)

def main(args):
    graph = AudioGraph()

    break_player = BreakPlayer("../audio/amen-brother.wav")
    break_player.play()

    def yaw_handler(_, yaw):
        print("yaw: %s" % yaw)
    def pitch_handler(_, pitch):
        print("pitch: %s" % pitch)
        cutoff = scale_lin_lin(pitch, 0, 1, 10, 10000)
        break_player.set_input("cutoff", cutoff)
    def roll_handler(_, roll):
        print("roll: %s" % roll)

    dispatcher = Dispatcher()
    dispatcher.map("/yaw", yaw_handler)
    dispatcher.map("/pitch", pitch_handler)
    dispatcher.map("/roll", roll_handler)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(args)