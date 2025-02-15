#!/usr/bin/env python3

import VL53L1X
from pythonosc.udp_client import SimpleUDPClient
from signalflow import *
import signal


class Theremin (Patch):
    def __init__(self):
        super().__init__()
        frequency = self.add_input("frequency")
        amplitude = self.add_input("amplitude")
        frequency = Smooth(frequency, 0.999)
        square = SquareOscillator(frequency)
        filtered = SVFilter(square, "low_pass", frequency)
        stereo = StereoPanner(filtered) * amplitude * 0.2
        delayed = CombDelay(stereo, 0.1, feedback=0.8)
        output = stereo + delayed
        self.set_output(output)

def main():
    tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
    tof.open()
    tof.set_inter_measurement_period(20)
    tof.set_timing_budget(10000)
    running = True

    def exit_handler(signal, frame):
        nonlocal running
        running = False

    # Attach a signal handler to catch SIGINT (Ctrl+C) and exit gracefully
    signal.signal(signal.SIGINT, exit_handler)

    #--------------------------------------------------------------------------------
    # Ranging mode can be SHORT, MEDIUM, LONG
    #--------------------------------------------------------------------------------
    tof.start_ranging(VL53L1X.VL53L1xDistanceMode.MEDIUM)

    graph = AudioGraph()
    theremin = Theremin()
    theremin.play()

    while running:
        distance = tof.get_distance()
        frequency = scale_lin_exp(distance, 50, 300, 40, 8000)
        print(f"Distance: {distance} mm, frequency: {frequency} Hz")
        amplitude = 1 if distance > 0 else 0
        theremin.set_input("frequency", frequency)
        theremin.set_input("amplitude", amplitude)
    tof.stop_ranging()

if __name__ == "__main__":
    main()
