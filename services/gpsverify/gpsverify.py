#!/usr/bin/python3

from time import sleep # For sleeping between dbus messages
import sys             # Used to exit in error conditions and flushing the buffer
import os              # Used for reading envrion vars
import json            # For reading test_points.log file
import datetime        # For converting posix timestamp to epoc
import math            # For converting x and y error to total hoiz error
import postgres        # For checking that the data was properly uploaded

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
        print("tuple argument for gps_to_dbus was not valid. Expected 15 entries, got",len(dbusargs))
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

print('Waiting 10s for gps2tsdb and postgres to startup')
sleep(10)


print('Connecting to the database')
connectionurl='postgresql://' + os.environ['db_user'] + ':' + os.environ['db_password'] + '@postgres:' + os.environ['db_port'] + '/' + os.environ['db_database']
print("Initing Postgres obj")
db = postgres.Postgres(url=connectionurl)

# This should be replaced query that deletes all lines from the device "fake gps" or whatever but until
# gps device is recorded this is what we got 
db.run("TRUNCATE gps;")

with open(testpointsloc) as f:
    for line in f:
        point = ''
        try:
             point = json.loads(line)
        except ValueError as e:
             continue;
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
            # Check database that point was added
            rst = db.one("SELECT * FROM gps where time = %s;", (point['time'],) )
            if rst is not None and len(rst) == 3 and rst.lat == point['lat'] and rst.lng == point['lon']:
              print('Timestamp', point['time'], 'successful')
            else:
              print('Line', line, '\nwas not successfully entered into database!\ndb entry:', rst)
              sys.exit(-1)
            sys.stdout.flush()
print("All points successfully inserted into database. Exiting")
