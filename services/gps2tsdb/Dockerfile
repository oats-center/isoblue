# BUILDER
FROM python:3 as builder

WORKDIR /usr/src/app

# Download latest listing of available packages:
RUN apt-get -y update

# Install packages required for DBUS dependencies

# Needed for building dbus
RUN apt-get install -y --no-install-recommends python3-dbus libdbus-glib-1-dev libdbus-1-dev

# Needed for building PyGObject
RUN apt-get install -y --no-install-recommends libgirepository1.0-dev gcc pkg-config python3-dev gir1.2-gtk-3.0

COPY requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt


# RUNTIME
FROM python:3 as runtime

# Install runtime deps
RUN apt-get -y update && apt-get install -y --no-install-recommends python3-dbus

WORKDIR /usr/src/app
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

COPY gps.py .
CMD [ "python", "./gps.py" ]
