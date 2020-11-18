# BUILDER
FROM python:3 as builder

WORKDIR /usr/src/app

# Download latest listing of available packages
RUN apt-get -y update

# Needed for building dbus
RUN apt-get install -y --no-install-recommends python3-dbus libdbus-glib-1-dev libdbus-1-dev

# Needed for building PyGObject
RUN apt-get install -y --no-install-recommends libgirepository1.0-dev gcc pkg-config python3-dev gir1.2-gtk-3.0

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

# Install runtime deps
# Last two are needed for switch to slim
RUN apt-get -y update && apt-get install -y --no-install-recommends python3-dbus \
    libgirepository-1.0-1 gir1.2-gtk-3.0

# Copy compiled venv from builder
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy health check script
COPY healthcheck.py .
HEALTHCHECK CMD ["python", "./healthcheck.py"]

# Copy script over and run
COPY gps.py .
CMD [ "python", "./gps.py" ]
