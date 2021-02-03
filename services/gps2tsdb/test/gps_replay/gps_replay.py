#!/usr/bin/python3

from time import sleep # For sleeping between dbus messages
import sys             # Used to exit in error conditions and flushing the buffer
import os              # Used for reading envrion vars
import json            # For reading test_points.log file
import datetime        # For converting posix timestamp to epoc
import math            # For converting x and y error to total hoiz error
import zmq             # For publishing gps points for verification containers

# For interacting with dbus to send messages
from jeepney import DBusAddress, new_signal
from jeepney.integrate.blocking import connect_and_authenticate

# Location of log file to insert into database
testpointsloc = '/opt/test_points.log'

# Equivalent to 
#
# sudo dbus-send --system --type=signal /org/gpsd org.gpsd.fix \
# double:{Seconds since unix epoc} \
# int32:{mode} \     
# double:{time uncertainty (seconds)} \  
# double:{Lat in deg} \ 
# double:{Lng in deg} \
# double:{Horiz uncertainty} \ 
# double:{Altitude} \
# double:{Altitude uncertainty} \ 
# double:{Course in deg from true north} \
# double:{Course uncertainty} \    
# double:{Speed} \
# double:{Speed uncertainty} \     
# double:{Climb} \
# double:{Climb uncertainty} \   
# string:{Device name}

# Based off this blocking example from jeepney docs found here: 
#   https://jeepney.readthedocs.io/en/latest/integrate.html
def gps_to_dbus(dbusargs):
    if len(dbusargs) != 15:
        print('tuple argument for gps_to_dbus was not valid. Expected 15 entries, got',len(dbusargs))
        return -1

    gps = DBusAddress('/org/gpsd',
                       bus_name=None,
                       interface='org.gpsd')

    connection = connect_and_authenticate(bus='SYSTEM')

    # Construct a new D-Bus message. new_method_call takes the address, the
    # method name, the signature string, and a tuple of arguments.
    # 'signature string' is not documented well, it's basically the argument types. More info here
    #    https://dbus.freedesktop.org/doc/dbus-specification.html#type-system
    msg = new_signal(gps, 'fix', 'didddddddddddds', dbusargs )

    # Send the message and wait for the reply
    reply = connection.send_message(msg)
    #print('Reply: ', reply)

    connection.close()

if not os.path.isfile(testpointsloc):
    print('Test points file does not exist in', testpointsloc, ', cannot insert test points')
    exit(-1)

print('Setting up zeromq')
# Modified example from https://zguide.zeromq.org/docs/chapter2/#Node-Coordination
subs_expected = 1
zmq_ctx = zmq.Context()

# Socket to talk to clients
zmq_pub = zmq_ctx.socket(zmq.PUB)
# set SNDHWM, so we don't drop messages for slow subscribers
zmq_pub.sndhwm = 1100000
zmq_pub.bind('tcp://*:5561')

# Socket to receive signals
zmq_sync = zmq_ctx.socket(zmq.REP)
zmq_sync.bind('tcp://*:5562')

# Get synchronization from subscribers
print('awaiting', subs_expected, 'subs')
subscribers = 0
while subscribers < subs_expected:
    # wait for synchronization request
    msg = zmq_sync.recv()
    # send synchronization reply
    zmq_sync.send(b'')
    subscribers += 1
    print('+1 subscriber (%i/%i)' % (subscribers, subs_expected))

with open(testpointsloc) as f:
    for line in f:
        point = ''
        try:
             point = json.loads(line)
        except ValueError as e:
             continue
        # Read the line in as JSON and convert it to python object
        point = json.loads(line)
        # Skip points that do not have a full 3D fix 
        if point['class'] == 'TPV' and point['mode'] == 3:

            # Convert ISO time string into posix epoch time
            timeraw = point['time']
            if timeraw[-1] == 'Z':
              timeraw = timeraw[:-1]
            time_epoch = datetime.datetime.fromisoformat(timeraw).timestamp()


            # So this gets really nasty. Basically we have a list of key-value pairs and we need to put the values into an ordered tuple.
            # We are not guaranteed the order or even existence of any given key (I am assuming that time, mode, and device will always exist as the 
            # points are pretty useless without time plus mode and device _should_ always be known as they are independent of the device having a gps fix). 
            # If the key does not exist 'NaN' should be inserted instead
            # I am creating a list that I will insert each item from the json tuple into and then convert into a tuple. I check for the existence of each
            # point and insert nan or the point. There may be a better way. I considered a tuple of all the keys and then iterating through them but some
            # points require special attention (ex altitude). Mappings were found from here: https://gitlab.com/gpsd/gpsd/-/blob/release-3.20/dbusexport.c#L55
            #  At some point the data log should be modified to add extreme values as well

            dbuslist = []
            dbuslist.append(time_epoch)

            dbuslist.append(point['mode'])
            if 'ept' in point:
                dbuslist.append(point['ept'])
            else:
                dbuslist.append(float('nan'))

            if 'lat' in point:
                dbuslist.append(point['lat'])
            else:
                dbuslist.append(float('nan'))

            if 'lon' in point:
                dbuslist.append(point['lon'])
            else:
                dbuslist.append(float('nan'))

            if 'eph' in point:
                dbuslist.append(point['eph'])
            else: 
                dbuslist.append(float('nan'))

            if 'alt' in point:
                dbuslist.append(point['alt'])
            elif 'altMSL' in point:
                dbuslist.append(point['altMSL'])
            else:
                dbuslist.append(float('nan'))

            if 'epv' in point:
                dbuslist.append(point['epv'])
            else:
                dbuslist.append(float('nan'))

            if 'track' in point:
                dbuslist.append(point['track'])
            else:
                dbuslist.append(float('nan'))

            if 'epd' in point:
                dbuslist.append(point['epd'])
            else:
                dbuslist.append(float('nan'))

            if 'speed' in point:
                dbuslist.append(point['speed'])
            else:
                dbuslist.append(float('nan'))

            if 'eps' in point:
                dbuslist.append(point['eps'])
            else:
                dbuslist.append(float('nan'))
	
            if 'climb' in point:
                dbuslist.append(point['climb'])
            else:
                dbuslist.append(float('nan'))

            if 'epc' in point:
                dbuslist.append(point['epc'])
            else:
                dbuslist.append(float('nan'))

            # Using a constant to ensure this is never confused for real data
            dbuslist.append('fake-data-verification')

            # convert to tuple to send to dbus method
            tup = tuple(dbuslist)
		    
            print('Tuple:', tup)
            gps_to_dbus(tup)
        
            # Don't overpower gps2tsdb
            sleep(.1)

            # Publish GPS point to zeromq
            print('Publishing gps data')
            zmq_pub.send_json(point)
            sys.stdout.flush()

print('Sending end messages')
zmq_pub.send_json(json.dumps("END"))

print('All points successfully inserted into database. Staying alive so that exit code for gps_verify is used')
while(True):
    sleep(10000)
