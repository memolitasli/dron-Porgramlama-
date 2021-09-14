#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dronekit import VehicleMode, connect,LocationGlobalRelative,Vehicle,Command, mavlink

drone = connect(wait_ready=True)
while True:
    print("altitude : " + str(drone.location.global_relative_frame.alt))