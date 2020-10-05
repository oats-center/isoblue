#!/usr/bin/python3
import postgres
import sys
import os
import datetime

threshold = 5

connectionurl='postgresql://' + os.environ['db_user'] + ':' + os.environ['db_password'] + '@postgres:' + os.environ['db_port'] + '/' + os.environ['db_database']
db = postgres.Postgres(url=connectionurl)

rst = db.one("SELECT * FROM gps ORDER BY time DESC LIMIT 1;")

if rst == None:
    print("Database has the wrong schema or no data");
    sys.exit(1)

lastupdate = rst[0]
tdelta = datetime.datetime.now(lastupdate.tzinfo) - lastupdate
sdelta = tdelta.total_seconds()
if sdelta > threshold:
  print('Database was last updated', sdelta, 'seconds ago, something is wrong ( threshold:', threshold, 's )');
  sys.exit(1)

print('Database was last updated', sdelta, 'seconds ago, everything is normal ( threshold:', threshold, 's )');
