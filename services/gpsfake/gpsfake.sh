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
#cat /usr/share/dbus-1/system.conf

#Sleep for 10s to allow gps2tsdb and the database to start up
echo "Sleeping 10 to allow startup"
sleep 10

echo "Starting dbus-monitor in the background"
#dbus-monitor --system "interface='org.gpsd'" &
#tcpdump -s0 -n -A -i lo udp and port 5000 &

# Run GPS fake
echo "Starting gpsfake"
gpsfake -1 -l -S -n -D 2 fake-gps.log
