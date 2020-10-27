#!/bin/sh

# Setup dbus
# Taken from here: https://georgik.rocks/how-to-start-d-bus-in-docker-container/

# Generate missing machine-id by command
#echo "Generating missing machine-ids"
#dbus-uuidgen > /var/lib/dbus/machine-id

# Start the D-Bus daemon inside the container
# The output should look like this
#echo "Starting dbus daemon"
#mkdir -p /var/run/dbus
#dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address

#Sleep for 10s to allow gps2tsdb and the database to start up
sleep 10

# Run GPS fake
echo "Starting gpsfake"
gpsfake -l -S fake-gps.log
