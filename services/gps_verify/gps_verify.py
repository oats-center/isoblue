#!/usr/bin/python3
import zmq
import postgres
import time
import os
import sys
import json
from pynng import Sub0, Req0

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
print('Connecting to zmq sub socket')
subscriber = context.socket(zmq.SUB)
subscriber.connect('tcp://gps_replay:5561')
subscriber.setsockopt(zmq.SUBSCRIBE, b'')

time.sleep(1)

# Second, synchronize with publisher
print('Connecting to zmq sync socket')
syncclient = context.socket(zmq.REQ)
syncclient.connect('tcp://gps_replay:5562')

# send a synchronization request
print('Sending sync zmq request')
syncclient.send(b'')

# wait for synchronization reply
print('Awaiting zmq sync reply')
syncclient.recv()

print('Setting up nng')
nngreq = Req0(dial='tcp://gps_replay:6662')

print('Sending sync nng request')
nngreq.send(b'SYN')

print('Awaiting nng sync reply')
nngreq.recv()

print('Connecting to nng sub socket')
nngsub = Sub0(dial='tcp://gps_replay:6661')
nngsub.subscribe(b'')

# Third, get our updates and report how many we got
points_received = 0
while True:
  print('Awaiting zmq gps point')
  
  zmqpoint = subscriber.recv_json()
  print('Awaiting nng gps point')
  
  nngpoint = json.loads(nngsub.recv().decode('utf-8'))

  if zmqpoint == json.dumps("END") and nngpoint == "END":
    break

  print('Verifying that zmq', zmqpoint['time'], ' is in the database')
  
  rst = db.one('SELECT * FROM gps where time = %s;', (zmqpoint['time'],) )
  if rst is not None and len(rst) == 3 and rst.lat == zmqpoint['lat'] and rst.lng == zmqpoint['lon']:
    print('zmq timestamp', zmqpoint['time'], 'successfully entered into the database')
    points_received

  else:
    print('zmq GPS point', zmqpoint, '\nwas not successfully entered into database!\ndb entry:', rst)
    sys.exit(-1)
  
  print('Verifying that zmq', nngpoint['time'], ' is in the database')
  rst = db.one('SELECT * FROM gps where time = %s;', (nngpoint['time'],) )
  if rst is not None and len(rst) == 3 and rst.lat == nngpoint['lat'] and rst.lng == nngpoint['lon']:
    print('zmq timestamp', nngpoint['time'], 'successfully entered into the database')
    points_received

  else:
    print('zmq GPS point', nngpoint, '\nwas not successfully entered into database!\ndb entry:', rst)
    sys.exit(-1)
  
  points_received = points_received + 1
  sys.stdout.flush()

print('Successfully verified %d points' % points_received)