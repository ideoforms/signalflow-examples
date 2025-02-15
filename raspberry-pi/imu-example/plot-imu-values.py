#!/usr/bin/env python

import time
import math
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("192.168.1.22", 12000)

from icm20948 import ICM20948

imu = ICM20948()

client.send_message("/add_panel", ["ax"])
client.send_message("/add_panel", ["ay"])
client.send_message("/add_panel", ["az"])
client.send_message("/add_panel", ["gx"])
client.send_message("/add_panel", ["gy"])
client.send_message("/add_panel", ["gz"])

while True:
# x, y, z = imu.read_magnetometer_data()
    ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()
    client.send_message("/data", ["ax", ax])
    client.send_message("/data", ["ay", ay])
    client.send_message("/data", ["az", az])
    client.send_message("/data", ["gx", gx])
    client.send_message("/data", ["gy", gy])
    client.send_message("/data", ["gz", gz])

    time.sleep(0.01)
