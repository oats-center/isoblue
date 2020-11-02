#!/usr/bin/python3

from time import sleep # For sleeping between rx_bytes checks
import sys             # Used to exit if no CAN interfaces are found
import os              # Used to list /sys/class/net directory, reading envrion vars

# For interacting with dbus to request system sleep
from jeepney import DBusAddress, new_signal
from jeepney.integrate.blocking import connect_and_authenticate


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
        print("Tuple argument for gps_to_dbus was not valid. Expected 15 entries, got",len(dbusargs))
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


sleep(10)
arg = (1.6041e+09 ,3 ,0.005 ,40.4295 ,-86.9124 ,150.935 ,215.974 ,198.49 ,96.4534 ,float('nan') ,0.06926 ,0.59 ,0.0245572 ,396.98 ,"/dev/Neust")

gps_to_dbus(arg)
