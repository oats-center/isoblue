#!/usr/bin/python3

# DBUS imports
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
import dbus

# Postgres imports
import postgres

# Environmental variable reading
import os.environ


# Process GPS data, called every time a fix is acquired
def fix(*args):
    # Data comes in as an array, extract the relevant data. See the DBUS section of `man 8 gpsd` for more information
    time = float(args[0])
    lat = float(args[3])
    lng = float(args[4])

    # Print it all out for debugging
    print("Time: ", time, "\tLat: ", lat, "\tLng: ", lng)
    print("Inserting lat and lng for timestamp", time)
    # Insert into database using global db var
    db.run("INSERT INTO gps (time, lat, lng) VALUES (to_timestamp(%s), %s, %s)", (time, lat, lng) )
    print("Finished inserting lat and lng for timestamp ", time)


# Create global db var and connection url using environmental variables passed in from docker
global db
connectionurl='postgresql://' + os.environ['db_user'] + ':' + os.environ['db_password'] + '@postgres:' + os.environ['db_port'] + '/' + os.environ['db_database']
print("Initing Postgres obj")
db = postgres.Postgres(url=connectionurl)

# Ensure DB is setup as required
print("Ensuring timescaledb extension is activated")
db.run("CREATE EXTENSION IF NOT EXISTS timescaledb;")
print("Ensuring tables are setup properly")
db.run("""
        CREATE TABLE IF NOT EXISTS gps (
          time timestamptz UNIQUE NOT NULL,
          lat double precision NOT NULL,
          lng double precision NOT NULL);""")
print("Ensuring GPS point table is a timescaledb hypertable")
db.run("SELECT create_hypertable('gps', 'time', if_not_exists => TRUE, migrate_data => TRUE);")
print("Finished settting up tables")

# Setup DBUS reading and use fix() as a callback whenever a fix is received
DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
bus.add_signal_receiver(fix, signal_name='fix', dbus_interface="org.gpsd")

loop = GLib.MainLoop()
loop.run()
