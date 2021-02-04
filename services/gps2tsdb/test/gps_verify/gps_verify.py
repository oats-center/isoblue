#!/usr/bin/python3
import postgres
from psycopg2 import OperationalError
import time
import os
import sys
import json
import asyncio         
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

points_received = 0

async def run(loop):
  
  print('Connecting to the database')
  connectionurl='postgresql://' + os.environ['db_user'] + ':' + os.environ['db_password'] + '@postgres:' + os.environ['db_port'] + '/' + os.environ['db_database']

  # Try to connect to the DB. It may be starting up so we should try a few timees
  # before failing. Currently trying every second 60 times
  tries = 0
  maxtries = 60
  sleeptime = 1
  db_connected = False
  while not db_connected:
    try:
      db = postgres.Postgres(url=connectionurl)
    except OperationalError as e:
      if tries < maxtries:
        print("Database connection attempt", tries, "failed. Database may still be starting. Sleeping", sleeptime, "s and trying again")
        print(e)
        tries = tries + 1
        time.sleep(sleeptime)
      else:
        print("FATAL: Could not connect to db after", tries, "tries. Exiting")
        sys.exit(-1)
    else:
      print("DB successfully connected")
      db_connected = True

  # Sleep for 2 seconds to allows gps2tsdb to create the gps table
  time.sleep(5)

  # This should be replaced query that deletes all lines from the device 'fake gps' or whatever but until
  # gps device is recorded this is what we got 
  print('Truncating GPS database')
  db.run('TRUNCATE gps;')
    
  print('Setting up NATS')
  # Connect to NATS server 
  nc = NATS()
  await nc.connect("nats://nats:4222")
  
  # Notifies the non-callback function that we are finished
  fin = asyncio.Future() 

  async def message_handler(msg): 
    nats_gps_point = json.loads(msg.data.decode())

    # Debugging
    #print("NATS type:", type(nats_gps_point), "\nmessage:", nats_gps_point)
    
    # Check if this is a control message signifying the end of the transmission
    if nats_gps_point == "END": 
      print('End control message received. No more gps points to check')
      nonlocal fin
      fin.set_result("END")
      return

    # Check for NAT's point
    print('Verifying that nats', nats_gps_point['time'], ' is in the database')
    rst = db.one('SELECT * FROM gps where time = %s;', (nats_gps_point['time'],) )
    if rst is not None and len(rst) == 3 and rst.lat == nats_gps_point['lat'] and rst.lng == nats_gps_point['lon']:
      print('nats timestamp', nats_gps_point['time'], 'successfully entered into the database')
    else:
      print('nats GPS point', nats_gps_point, '\nwas not successfully entered into database!\ndb entry:', rst)
      sys.exit(-1)
      
    # Counter just for fun
    global points_received
    points_received = points_received + 1
    sys.stdout.flush()
    return


  print("setting up gps message callback")
  sid = await nc.subscribe("gps", cb=message_handler)
  print("gps message callback setup")
  sys.stdout.flush()
  
  await nc.flush(1)

  await fin
  print("End message received. Exiting")
  await nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
    
    print('Successfully verified %d points' % points_received)
    sys.exit(0)

