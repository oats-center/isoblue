#!/usr/bin/env python3

import sys
import json
import configparser 

from gps3 import gps3

import sqlite3

import time
from datetime import datetime

cfgpath = '/opt/isoblue/isoblue.cfg'

debuglevel = 100

# Custom debug level. Set a debug level when calling which will be compared to the system
#   debug level when determining to print or not
def printdebug(lvl=2, *args, **kwargs):
    if lvl <= debuglevel:
        print('DEBUG ' + str(lvl) + ': ', *args, file=sys.stderr, **kwargs)


def readconfig( config_parser, configdict ):
    
    # Read config file
    filesread = config.read(cfgpath)

    # Verify config read correctyly
    if filesread[0] != cfgpath:
        printdebug(1, 'Could not read config file')
        exit(-1)

    # Read in relevant config options
    configdict['debuglevel'] = config.get('ISOBlue', 'debuglevel')
    configdict['isoblue_id'] = config.get('ISOBlue', 'id')
    configdict['dbpath'] = config.get('ISOBlue', 'dbpath')
    configdict['baseuri'] = config.get('REST', 'baseuri') + '/' + configdict['isoblue_id'] + '/GPS/day-index'
    
    printdebug(2, 'Config file read success:')
    printdebug(2, '\tDebug Level: ', configdict['debuglevel'])
    printdebug(2, '\tISOBlue ID: ', configdict['isoblue_id'])
    printdebug(2, '\tdbpath: ', configdict['dbpath'])
    printdebug(2, '\tbaseuri: ', configdict['baseuri'])


if __name__ == "__main__":

    printdebug(2, 'Starting up')

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


    # Setup gpsd
    s = gps3.GPSDSocket()
    s.connect(host='127.0.0.1', port=2947)
    s.watch()

    timestamp = None
    last_tpv_timestamp = None

    # Reparse the config file for any changes every n iterations
    updateconfigcountdown = 1000

    # Catch Ctrl-C to gracefully shutdown
    try:
        # For each data given by gpsd socket
        for data in s:
            if data:
                new_data = json.loads(data)
                object_name = new_data.pop('class', 'ERROR')
                
                # Holder for data to send (SKY or TPV or etc)
                data = None

                # convert 'n/a' to None for proper
                for key, value in new_data.items():
                    if value == 'n/a':
                        new_data[key] = None
            
                # the object should be TPV now
                if object_name == 'TPV':
                    if 'time' and 'lon' and 'lat' in new_data:
                        utc_dt = datetime.strptime(new_data['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        timestamp = int((utc_dt - datetime(1970, 1, 1)).total_seconds())
                        new_data['time'] = timestamp
                        
                        lng = new_data['lon']
                        lat = new_data['lat']
                        
                        # Construct uri and json to send
                        # data format: {"sec-index":{"1571951029":{"lat":40.4295435,"lng":-86.912788167}}}
                        #data = json.dumps( { 'sec-index': { timestamp : { 'lat': lat, 'lng': lng,}, },} )

                        # This is not yet valid json, but when we batch it the 'sec-index' bit will be added and it will become valid
                        data = '\"' + str(timestamp)+ '\":{\"lat\":' + str(lat) + ',\"lng\":' + str(lng) + '}'

 
                    last_tpv_timestamp = timestamp
                   
                # the object should be SKY
                elif object_name == 'SKY':
                    # do we need anything else?
                    pass
                # the object should be PPS 
                elif object_name == 'PPS':
                    # do we need anything else?
                    pass
                # ditch other samples
                else:
                    continue

                
                if data is not None:
                    # Create URI for uploading to OADA server
                    uri = configdict['baseuri'] + '/' + datetime.now().isoformat()[:10] + '/hour-index/' + str(time.localtime(time.time()).tm_hour)


                    printdebug(2, 'Attempting to insert ', (int(time.time()), uri, data, 0), ' into database')

                    # Publish the following data to the db:
                    # Time: Current UNIX time
                    # Topic: URI to upload to OADA server
                    # Payload: 'JSON' GPS Data
                    db.cursor().execute(''' INSERT INTO sendqueue(time, topic, data, sent)
                                            VALUES(?,?,?,?)''', (int(time.time()), uri, data, 0) )
                    db.commit()
            data = None
            
            # decrement update counter
            updateconfigcountdown = updateconfigcountdown - 1
            # if counter reaches 0, update the config and reset the counter
            if updateconfigcountdown <= 0:
                readconfig( config, configdict )
                updateconfigcountdown = 100

            time.sleep(0.1)



    except KeyboardInterrupt:
        printdebug(2, 'Ctrl-C caught, exiting')
        # Close connection to db
        db.close()
        s.close()
