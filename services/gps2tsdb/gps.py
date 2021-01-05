#!/usr/bin/python3
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import postgres
import os
from prometheus_client import start_http_server, Gauge
import sys
from time import sleep
from psycopg2 import OperationalError

def fix(*args):
    #print(args)
    print("Time: ", args[0], "\tLat: ", args[3], "\tLng: ", args[4])
    lat_gauge.set(args[3])
    lng_gauge.set(args[4])
    time_gauge.set(args[0])

    print("Inserting lat and lng for timestamp ", args[0])
    db.run("INSERT INTO gps (time, lat, lng) VALUES (to_timestamp(%s), %s, %s)", (float(args[0]), float(args[3]), float(args[4]) ) )
    print("Finished inserting lat and lng for timestamp ", args[0])
    sys.stdout.flush()

# Prometheus variables to export
global lat_gauge
lat_gauge = Gauge('avena_position_lat', 'Last know fix latitude')
global lng_gauge
lng_gauge = Gauge('avena_position_lng', 'Last know fix longitude')
global time_gauge
time_gauge = Gauge('avena_position_time', 'Last know fix time')
start_http_server(10001)

global db
connectionurl='postgresql://' + os.environ['db_user'] + ':' + os.environ['db_password'] + '@postgres:' + os.environ['db_port'] + '/' + os.environ['db_database']
print("Initing Postgres obj")


# Try to connect to the DB. It may be starting up so we should try a few timees
# before failing. Currently trying every second 60 times
tries = 0
maxtries = 60
sleeptime = 1
db_connected = False
while(not db_connected):
  try:
    db = postgres.Postgres(url=connectionurl)
  except OperationalError as e:
    if( tries < maxtries):
      print("Database connection attempt", tries, "failed. Database may still be starting. Sleeping", sleeptime, "s and trying again")
      print(e)
      tries = tries + 1
      sleep(sleeptime)
    else:
      print("FATAL: Could not connect to db after", tries, "tries. Exiting")
      sys.exit(-1)
  else:
    db_connected = True

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
sys.stdout.flush()

print("Setting up DBUS")
DBusGMainLoop(set_as_default=True)
tries = 0
maxtries = 60
dbus_connected = False
while(not dbus_connected):
  try:
    bus = dbus.SystemBus()
  except dbus.exceptions.DBusException as e:
    if( tries < maxtries):
      print("DBUS connection failed. This may be the case in a testing environment where dbus is being setup concurrently. Sleeping ", sleeptime, "s and trying again")
      maxtries = maxtries + 1
      sleep(sleeptime)
    else:
      print("FATAL: Could not connect to dbus after,", tries, ". Last error was",e,"Exiting")
      sys.exit(-1)
  else:
    dbus_connected = True

bus.add_signal_receiver(fix, signal_name='fix', dbus_interface="org.gpsd")

loop = GLib.MainLoop()
loop.run()
