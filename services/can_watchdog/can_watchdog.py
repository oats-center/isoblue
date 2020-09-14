#!/usr/bin/python3

from time import sleep # For sleeping between rx_bytes checks
import sys             # Used to exit if no CAN interfaces are found
import os              # Used to list /sys/class/net directory, reading envrion vars

# For interacting with dbus to request system sleep
from jeepney import DBusAddress, new_method_call
from jeepney.integrate.blocking import connect_and_authenticate


# Equalivent to 
#   `sudo dbus-send --system --print-reply --dest="org.freedesktop.login1" \
#      /org/freedesktop/login1 org.freedesktop.login1.Manager.Suspend boolean:true`
# or 
#   `systemctl suspend`
# Based off this blocking example from jeepney docs found here: 
#   https://jeepney.readthedocs.io/en/latest/integrate.html
def suspend_with_dbus():
    suspend = DBusAddress('/org/freedesktop/login1',
                            bus_name='org.freedesktop.login1',
                            interface='org.freedesktop.login1.Manager')

    connection = connect_and_authenticate(bus='SYSTEM')

    # Construct a new D-Bus message. new_method_call takes the address, the
    # method name, the signature string, and a tuple of arguments.
    # 'signature string' is not documented well, it's bascally the argument types. More info here
    #    https://dbus.freedesktop.org/doc/dbus-specification.html#type-system
    msg = new_method_call(suspend, 'Suspend', 'b', (True, ) )

    # Send the message and wait for the reply
    reply = connection.send_and_get_reply(msg)
    print('Reply: ', reply)

    connection.close()



print('CAN Watchdog has started')
print('Gathering all can interfaces')

rx_paths = []

# Where the host '/sys/class/net/' dir is mounted in the container
sysclass = '/mnt/host/sys/class/net/'

# How long to sleep betweeen rx_bytes checks. Default to 5
check_interval = 5
if os.environ['inactivity_threshold'].strip().isdigit():
    check_interval = int(os.environ['inactivity_threshold'].strip())
else:
    print('inactivity threshold value `', os.environ['inactivity_threshold'].strip(), '` could not be coerced into an int, using default value')

# Iterate through all links listed in /sys/class/net
for network in os.listdir(sysclass):

    # This file defines the type of the network
    path = sysclass + network + '/type'
    print('Checking network ', network, ' type at path ', path)

    # Sometimes things are not setup like we expect. Live and let live
    if not os.path.isfile(path):
        print(network, ' does not have a type file. Skipping')
        continue

    # Open the file and read it
    with open(path) as typefile:
        networktype = typefile.read().strip()

    # 280 is the type for CAN. 'Documentation' here:
    # https://elixir.bootlin.com/linux/latest/source/include/uapi/linux/if_arp.h#L56
    if networktype.isdigit() and int(networktype) == 280:
        print('\t', network, ' appears to be a CAN link')
        rx_paths.append(sysclass + network + '/statistics/rx_bytes')

if len(rx_paths) <= 0:
    print('FATAL: No CAN interfaces found')
    sys.exit(-1)

# Print found links
print(len(rx_paths), ' found: ', rx_paths)

prev_rx = 0
curr_rx = 0

# Make an array of the open file descriptors (objects?) so we don't have to reopen them every loop
rx_fds = []
for rx in rx_paths:
    rx_fds.append(open(rx, 'r'))

print('Setup complete. Waiting 60s and then beginning rx_bytes watch')
# Additional sleep to allow time for a human to login and disable the sleep function
sleep(60)

while True:
    print('Sleeping ',check_interval)
    sleep(check_interval)

    # Iterate through each fd. Each file should contain a single number
    for fd in rx_fds:
        fd.seek(0, 0)
        rx_str = fd.read().strip()

        # Ensure the file is the format we expect
        if rx_str.isdigit():
            curr_rx += int(rx_str)
        else:
            print('Could not coerce `', rx_str, '` to an integer, skipping') 
 
    print('rx bytes: ', curr_rx)

    # If there has been no change in bytes recieved since the last loop
    if curr_rx == prev_rx:
        print('Requesting suspend')
        suspend_with_dbus()

        # When we resume, lets wait a little bit longer just to let things settle down
        sleep(check_interval)
    else:
        prev_rx = curr_rx
        curr_rx = 0

    # Docker never seems to print stdout unless we manually flush it
    sys.stdout.flush()

