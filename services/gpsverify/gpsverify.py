#!/usr/bin/python3

from time import sleep # For sleeping between rx_bytes checks
import sys             # Used to exit if no CAN interfaces are found
import os              # Used to list /sys/class/net directory, reading envrion vars
import json            # For reading test_points.log file
import datetime        # For converting posix timestamp to epoc
import math            # For converting x and y error to total hoiz error

# For interacting with dbus to request system sleep
from jeepney import DBusAddress, new_signal
from jeepney.integrate.blocking import connect_and_authenticate

testpointsloc = '/opt/test_points.log'

# Equalivent to 
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
    # 'signature string' is not documented well, it's bascally the argument types. More info here
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
arg = (1.6041e+09 ,3 ,0.005 ,40.4295 ,-86.9124 ,150.935 ,215.974 ,198.49 ,96.4534 ,float('nan') ,0.06926 ,0.59 ,0.0245572 ,396.98 ,"/dev/Neust")

with open(testpointsloc) as f:
    for line in f:
        point = json.loads(line)
        #print('Line:', point)
        if point['class'] == 'TPV' and point['mode'] == 3:
            tm = point['time']
            if tm[-1] == 'Z':
              tm = tm[:-1]
            time_epoch = datetime.datetime.fromisoformat(tm).timestamp()


            # So this gets really nasty. Basically we have a list of key - value pairs that we need to put into an ordered tuple.
            # We are not guarenteed the order or even existence of any given key ( I am assuming that time, mode, and device will always exist as the 
            # points are pretty useless without time plus mode and device _should_ always be known as they are independed of the device habing a gps fix). 
            # If the key does not exist 'NaN' should be inserted instead
            # I am creating a list that I will insert each item from the json tuple into and then convert into a tuple. There may be a better way

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

            if 'epx' in point and 'epy' in point:
                horiz_uncertain = math.sqrt(math.pow(point['epx'], 2) + math.pow(point['epy'], 2))
                dbuslist.append(horiz_uncertain)
            else: 
                dbuslist.append(float('nan'))

            if 'alt' in point:
                dbuslist.append(point['alt'])
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

            dbuslist.append('test')

            tup = tuple(dbuslist)
		    
            print('Tuple:', tup)
            gps_to_dbus(tup)
        #else:
            #print("Not a TPV point with location data. Skipping")
        sys.stdout.flush()
        #sleep(1)
        
