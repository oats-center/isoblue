# RUNTIME
FROM debian:buster as runtime

# Install dbus for the dbus-daemon command
RUN apt-get -y update && apt-get install -y --no-install-recommends gpsd gpsd-clients

CMD sleep 1 && GPSD_HOME='/usr/sbin/' gpsfake -1 -c 1 -P 2948 /opt/test_points/test_points.log
