#!/usr/bin/env python3

import sys
sys.path.append('/opt/isoblue/lib')
import isoblue
import configparser 

import sqlite3

import time
from datetime import datetime
import socket

# For generating random string IDs
import string
import random

cfgpath = '/opt/isoblue/isoblue.cfg'

# Custom debug level. Set a debug level when calling which will be compared to the system
#   debug level when determining to print or not
debuglevel = 100

def printdebug(lvl=2, *args, **kwargs):
    if lvl <= debuglevel:
        print('DEBUG ' + str(lvl) + ': ', *args, file=sys.stderr, **kwargs)


def readconfig( config, configdict ):
    
    # Read config file
    filesread = config.read(cfgpath)

    # Verify config read correctyly
    if filesread[0] != cfgpath:
        printdebug(1, 'Could not read config file')
        exit(-1)

    # Read in relevant config options
    configdict['debuglevel'] = int(config.get('ISOBlue', 'debuglevel'))
    configdict['isoblue_id'] = config.get('ISOBlue', 'id')
    configdict['dbpath'] = config.get('ISOBlue', 'dbpath')
    configdict['hbinterval'] = int(config.get('ISOBlue', 'hbinterval'))
    configdict['baseuri'] = config.get('REST', 'baseuri') + '/' + configdict['isoblue_id'] + '/GPS/day-index'

    printdebug(2, 'Config file read success:')
    printdebug(2, '\tDebug Level: ', configdict['debuglevel'])
    printdebug(2, '\tISOBlue ID: ', configdict['isoblue_id'])
    printdebug(2, '\tdbpath: ', configdict['dbpath'])
    printdebug(2, '\thbinterval: ', configdict['hbinterval'])
    printdebug(2, '\tbaseuri: ', configdict['baseuri'])


def beat(db):
    # Update config (Nessicary every beat?)
    config = configparser.RawConfigParser()

    # Read config file
    configdict = {}
    readconfig( config , configdict )
   
    # Yes python, I really do want to modify a global
    global debuglevel
    debuglevel = configdict['debuglevel']

    # Heartbeat message vars
    currtime = time.time()
    cell_ns = float('-inf')
    wifi_ns = float('-inf')
    networkpresense = False
    systemhealthy = False
    unsentmessages = 0

    # Check for internet
    networkpresense = isoblue.internet()

    #TODO Check cell strength

    #TODO Check wifi strength

    #TODO Set LED Status lights (If applicable)

    # Ensure connection to db
    db = sqlite3.connect(configdict['dbpath'])

    # Execute count query
    cursor = db.cursor().execute('SELECT COUNT(sent) from sendqueue where sent == 0')
    unsentmessages = cursor.fetchall()[0][0] # TODO: Error checking

    uri = 'TODO'
    data = '\"' + str(isoblue.id_generator()) + '\":{\"time\":' + str(currtime) + ',\"cell_ns\":' + str(cell_ns) + ',\"wifi_ns\":' + str(wifi_ns) +\
        ',\"backlog\":' + str(unsentmessages) + ',\"netled\":' + str(networkpresense) + ',\"statled\":' + str(systemhealthy) + '}'

    printdebug(2, "Pushing then following data to the db: ", data)
    # Publish the following data to the db:
    # Time: Current UNIX time
    # Topic: URI to upload to OADA server
    # Payload: 'JSON' GPS Data
    db.cursor().execute(''' INSERT INTO sendqueue(time, topic, data, sent)
        VALUES(?,?,?,?)''', (int(time.time()), uri, data, 0) )
    db.commit()
    #TODO: ensure database is written to successfully
 

if __name__ == "__main__":
    # Catch Ctrl-C to gracefully shutdown
    try:
 
        printdebug(2, 'Heartbeat module starting up')

        # Setup config parser
        config = configparser.RawConfigParser()

        # Read config file
        configdict = {}
        readconfig( config , configdict )
        debuglevel = configdict['debuglevel']

        # Connect to database
        db = sqlite3.connect(configdict['dbpath'])
        # Create table if it does not alread exist
        db.cursor().execute('CREATE TABLE IF NOT EXISTS sendqueue(id INTEGER PRIMARY KEY, time INTEGER, topic TEXT, data TEXT, sent INTEGER)')
        db.cursor().execute('PRAGMA journal_mode=WAL')
        # Commit changes to db
        db.commit()

        
        while(True):
            # Main heartbeat function
            beat(db)  
            time.sleep(configdict['hbinterval'])

    except KeyboardInterrupt:
        printdebug(2, 'Ctrl-C caught, exiting')
        # Close connection to db
        db.close()