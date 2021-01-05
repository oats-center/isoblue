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
zmq_ctx = zmq.Context()

# First, connect our subscriber socket
print('Connecting to zmq sub socket')
zmq_sub = zmq_ctx.socket(zmq.SUB)
zmq_sub.connect('tcp://gps_replay:5561')
zmq_sub.setsockopt(zmq.SUBSCRIBE, b'')

time.sleep(1)

# Second, synchronize with publisher
print('Connecting to zmq sync socket')
zmq_sync = zmq_ctx.socket(zmq.REQ)
zmq_sync.connect('tcp://gps_replay:5562')

# send a synchronization request
print('Sending sync zmq request')
zmq_sync.send(b'')

# wait for synchronization reply
print('Awaiting zmq sync reply')
zmq_sync.recv()

# Third, get our updates and report how many we got
points_received = 0
while True:
  
  print('Awaiting zmq gps point')
  zmq_gps_point = zmq_sub.recv_json()

  # Check if this is a control message signifying the end of the transmission
  if zmq_gps_point == json.dumps("END"): 
    print('End control message received. No more gps points to check')
    break

  # Check for zmq's point
  print('Verifying that zmq', zmq_gps_point['time'], ' is in the database')
  rst = db.one('SELECT * FROM gps where time = %s;', (zmq_gps_point['time'],) )
  if rst is not None and len(rst) == 3 and rst.lat == zmq_gps_point['lat'] and rst.lng == zmq_gps_point['lon']:
    print('zmq timestamp', zmq_gps_point['time'], 'successfully entered into the database')
    points_received
  else:
    print('zmq GPS point', zmq_gps_point, '\nwas not successfully entered into database!\ndb entry:', rst)
    sys.exit(-1)
  
  # Counter just for fun
  points_received = points_received + 1
  sys.stdout.flush()

print('Successfully verified %d points' % points_received)
sys.exit(0)

