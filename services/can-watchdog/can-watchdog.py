#!/usr/bin/python3
import glob # For expanding wildcard filepaths
import jeepney # For interactions with dbus
from subprocess import call

print('CAN Watchtog has started')
print('Getting all can rx counters')
rx_paths = glob.glob('sys/class/net/can*/statistics/rx_bytes')
print(len(rx_paths), ' found: ', rx_paths)

prev_rx = 0
curr_rx = 0

sleep(5)

while True:
    for rx in rx_paths
        with open(rx, 'r') as file:
            curr_rx += int(file.read())
            
    if curr_rx == prev_rx:
        print('Requesting sleep')
        call(["systemctl", "suspend"])
    else:
        prev_rx = curr_rx

