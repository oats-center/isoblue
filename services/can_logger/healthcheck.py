#!/usr/bin/python3
import postgres
import sys
import os
from datetime import datetime
from time import sleep

# Take name of service, timestamp of last update, and threshold
# Compares the current time to the passed timestamp, and exits or outputs the appropriate message
# Not the most reusable function, but avoids copy and pasting the same code for both the csv and db checks
# If everything is okay, the function returns void, and if something is wrong it exits the program. Inconsistent
# but leads to concise code... Should consider changing in future
def checktimestamp(item, timestamp, threshold): 
    # Subtracting two datetimes gives a timedelta, we can convert this into an integer seconds
    delta = (datetime.now(lastupdate.tzinfo) - timestamp).total_seconds()
    if delta > threshold:
        print(item, 'was last updated', delta, 'seconds ago, something is wrong (threshold: ' + str(threshold) + 's)')
        sys.exit(1)

    print(item, 'was last updated', delta, 'seconds ago, everything is normal (threshold: ' + str(threshold) + 's)')


# If the time between the last update is larger than this threshold in seconds, change the status to unhealthy
threshold = 5

# Get environmental variable determining logging to csv or db or both
default_value = 'CSV'
log_env = os.getenv('CELL_LOG', default_value)
host_interfaces = os.environ['can_interface'].split(',')

for interface in host_interfaces:

    # Ensure that there is actually being data logged to the bus
    # Currently there are two hacky ways to do this. Either we can
    # check the amount of rx_bytes, write them to a file, and then
    # check for changes next time we run this script, or we can read
    # the file, sleep for a certain period of time, and then check again
    # Currently we are trying the later as it is a bit simpler although
    # slower to respond due to the sleep
    rx_start = -1
    rx_end = -1
    with open('/mnt/host/sys/class/net/' + interface + '/statistics/rx_bytes', 'r') as rx:
        rx_start = int(rx.read().strip())
        sleep(1)
        rx.seek(0,0)
        rx_end = int(rx.read().strip())
    
    print(interface, 'rx_end:', rx_end, 'rx_start:', rx_start)
    if (rx_end - rx_start) <= 0:
        print('No can messages sent on the bus, no expected action by can logger')
        continue
    '''
    rxbfile = interface + '_rx_bytes.tmp'
    if os.path.exists(rxbfile):
         with open(rxbfile, 'rw') as rxb_write, open('/mnt/host/sys/class/net/' + interface + '/statistics/rx_bytes', 'r') as rxb_read:
             old_read = int(rxb_write.read().strip())
             new_read = int(rxb_read.read().strip())
             old_read.write(str(new_read))
             if (new_read - old_read) <= 0:
                 print('No can messages sent on', interface, 'no expected action by logger')
                 continue


    else:
        with open(rxbfile, 'w') as rxb_write, open('/mnt/host/sys/class/net/' + interface + '/statistics/rx_bytes', 'r') as rxb_read:
            rxb_write(rxb_read().strip())
            print('Created temp file for next run with interface', interface)
            continue
    '''
    # If the container is logging to csv
    if 'CSV' in log_env.upper():
        logpath = '/data/log/' + interface + '.csv'
        # Ensure the file exists in the first place
        if not os.path.exists(logpath):
             print('Log file did not exist or was not able to be opened. Path: ',logpath)
             sys.exit(1)

        # Get the last time the file was modified
        lastupdate = datetime.fromtimestamp(os.path.getmtime(logpath))
        checktimestamp(logpath, lastupdate, threshold)

    # If the container is logging to database
    if 'DB' in log_env.upper():
        # Connect to the database
        connectionurl='postgresql://' + os.environ['db_user'] + ':' + os.environ['db_password'] + '@postgres:' + os.environ['db_port'] + '/' + os.environ['db_database']
        db = postgres.Postgres(url=connectionurl)

        # Query the most recent timestamp
        rst = db.one("SELECT * FROM can ORDER BY time where can_interface = ? DESC LIMIT 1;", interface)

        # Handle if the database is empty
        if rst == None:
            print("Database has the wrong schema or no data");
            sys.exit(1)

        # First column is the timestamp, in datetime format
        lastupdate = rst[0]
        checktimestamp(interface + ' CAN signal database table', lastupdate, threshold)

