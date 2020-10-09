#!/usr/bin/python3
import postgres
import sys
import os
from datetime import datetime

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
host_interface = os.environ['can_interface']

# If the container is logging to csv
if 'CSV' in log_env.upper():
    logpath = '/data/log/' + host_interface + '.csv'
    # Ensure the file exists in the first place
    if not os.path.exists(logpath):
         print('Log file did not exist or was not able to be opened')
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
    rst = db.one("SELECT * FROM can ORDER BY time DESC LIMIT 1;")

    # Handle if the database is empty
    if rst == None:
        print("Database has the wrong schema or no data");
        sys.exit(1)

    # First column is the timestamp, in datetime format
    lastupdate = rst[0]
    checktimestamp('CAN signal database table', lastupdate, threshold)

