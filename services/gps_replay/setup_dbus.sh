# Setup dbus
# Taken from here: https://georgik.rocks/how-to-start-d-bus-in-docker-container/

# Remove anything from the previous run
rm -r /var/run/dbus

# Generate missing machine-id by command
echo "Generating missing machine-ids"
dbus-uuidgen > /var/lib/dbus/machine-id

# Start the D-Bus daemon inside the container
echo "Starting dbus daemon"
mkdir -p /var/run/dbus

dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address

python ./gps_replay.py
