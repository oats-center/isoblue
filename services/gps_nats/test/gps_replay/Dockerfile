# RUNTIME
FROM debian:buster as runtime

# Install dbus for the dbus-daemon command
RUN apt-get -y update && apt-get install -y --no-install-recommends gpsd gpsd-clients

# Copy test points file and run
COPY ./test_points.log /opt/

CMD GPSD_HOME='/usr/sbin/' gpsfake -1 -c 1 -l -P 2948 /opt/test_points.log
