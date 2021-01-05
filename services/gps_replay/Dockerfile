# BUILDER
FROM python:3 as builder

WORKDIR /usr/src/app

# Activate virtualenv
RUN python -m venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and build with pip
COPY requirements.txt ./
RUN pip install -r requirements.txt



# RUNTIME
FROM python:3-slim as runtime

WORKDIR /usr/src/app

# Install dbus for the dbus-daemon command
RUN apt-get -y update && apt-get install -y --no-install-recommends dbus

# Copy compiled venv from builder
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy script over and run
COPY setup_dbus.sh .
COPY test_points.log /opt/
COPY gps_replay.py .

CMD ["bash", "./setup_dbus.sh"]
