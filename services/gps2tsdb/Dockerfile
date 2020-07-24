FROM python:3

WORKDIR /usr/src/app

# Download latest listing of available packages:
RUN apt-get -y update
# Install a new package:
RUN apt-get install -y apt-utils
RUN apt-get install -y python3-dbus libdbus-glib-1-dev libdbus-1-dev
RUN apt-get install -y libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
RUN ls /usr/lib/python3/dist-packages

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./gps.py" ]
