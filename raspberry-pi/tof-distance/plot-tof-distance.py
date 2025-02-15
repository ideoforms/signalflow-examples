#!/usr/bin/env python3

import VL53L1X
import time
from pythonosc.udp_client import SimpleUDPClient

tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open()
tof.set_inter_measurement_period(50)

client = SimpleUDPClient("192.168.1.22", 12000)

# Can be SHORT, MEDIUM, LONG
# tof.start_ranging(VL53L1X.VL53L1xDistanceMode.SHORT)
tof.start_ranging(VL53L1X.VL53L1xDistanceMode.LONG)
client.send_message("/add_panel", ["distance", 0.0, 0.0])

try:
    while True:
        distance = tof.get_distance()  # Returns distance in mm
        print(f"Distance: {distance} mm")
        client.send_message("/data", ["distance", float(distance)])
        time.sleep(0.01)
except KeyboardInterrupt:
    tof.stop_ranging()
