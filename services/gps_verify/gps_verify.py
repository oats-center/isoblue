#!/usr/bin/python3
import zmq
import postgres
import time
import os
import sys
import json

print('Waiting 10s for gps2tsdb and postgres to startup')
time.sleep(10)

print('Connecting to the database')
connectionurl='postgresql://' + os.environ['db_user'] + ':' + os.environ['db_password'] + '@postgres:' + os.environ['db_port'] + '/' + os.environ['db_database']
print('Initing Postgres obj')
db = postgres.Postgres(url=connectionurl)

# This should be replaced query that deletes all lines from the device 'fake gps' or whatever but until
# gps device is recorded this is what we got 
print('Truncating GPS database')
db.run('TRUNCATE gps;')

# Based on example from here: https://zguide.zeromq.org/docs/chapter2/#Node-Coordination

print('Setting up zeromq')
context = zmq.Context()

# First, connect our subscriber socket
print('Connecting to sub socket')
subscriber = context.socket(zmq.SUB)
subscriber.connect('tcp://gps_replay:5561')
subscriber.setsockopt(zmq.SUBSCRIBE, b'')

time.sleep(1)

# Second, synchronize with publisher
print('Connecting to sync socket')
syncclient = context.socket(zmq.REQ)
syncclient.connect('tcp://gps_replay:5562')

# send a synchronization request
print('Sending sync request')
syncclient.send(b'')

# wait for synchronization reply
print('Awaiting sync reply')
syncclient.recv()

# Third, get our updates and report how many we got
points_received = 0
while True:
  print('Awaiting gps point')
  point = subscriber.recv_json()
  if point == json.dumps("END"):
    break

  print('Verifying that', point['time'], ' is in the database')
  rst = db.one('SELECT * FROM gps where time = %s;', (point['time'],) )
  if rst is not None and len(rst) == 3 and rst.lat == point['lat'] and rst.lng == point['lon']:
    print('Timestamp', point['time'], 'successfully entered into the database')
    points_received

  else:
    print('GPS point', point, '\nwas not successfully entered into database!\ndb entry:', rst)
    sys.exit(-1)
  points_received = points_received + 1
  sys.stdout.flush()

print('Successfully verified %d points' % points_received)