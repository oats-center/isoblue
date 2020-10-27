# RUNTIME
FROM debian:buster

WORKDIR /usr/src/app

# Install runtime deps
# gpsd-clients causes a huge amount of dependencies which is not great. Likely becuase it 
# needs to interact with dbus via python which is the same problem we had
RUN apt-get -y update && apt-get install -y --no-install-recommends gpsd gpsd-clients dbus

# Copy health check script
#COPY healthcheck.py .
#HEALTHCHECK CMD ["python", "./healthcheck.py"]

# Copy over log to user as source 
COPY fake-gps.log . 
COPY gpsfake.sh . 
CMD [ "./gpsfake.sh" ]
