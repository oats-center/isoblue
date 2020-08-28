#!/usr/bin/python3

import glob # For expanding wildcard filepaths
from subprocess import call
from time import sleep
import sys

print('CAN Watchdog has started')
print('Getting all can rx_bytes counters')
rx_paths = glob.glob('/sys/class/net/can*/statistics/rx_bytes')
print(len(rx_paths), ' found: ', rx_paths)

prev_rx = 0
curr_rx = 0

rx_fds = []
for rx in rx_paths:
    rx_fds.append(open(rx, 'r'))

while True:
    print('Sleeping 5')
    sleep(5)
    for fd in rx_fds:
        fd.seek(0, 0)
        rx_str = fd.read().strip()
        if rx_str.isdigit():
            curr_rx += int(rx_str)
        else:
            print('Could not coerce `', rx_str, '` to an integer, skipping') 
 
    print('rx bytes: ', curr_rx)       
    if curr_rx == prev_rx:
        print('Requesting suspend')
        call(["systemctl", "suspend"])
        sleep(5)
    else:
        prev_rx = curr_rx
        curr_rx = 0

