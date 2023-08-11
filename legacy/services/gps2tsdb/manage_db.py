#!/usr/bin/python3

def setup_db_tables(db):
    print("Ensuring timescaledb extension is activated")
    db.run("CREATE EXTENSION IF NOT EXISTS timescaledb;")

    # There are many different objects that GPSD can return, however we are going
    # to stick with the 3 that the Purdue team has seen from the GPS modules that 
    # they use: TPV, SKY, and PPS. This could be easlily extended to include other 
    # objects if needed

    # Create GPS tpv table
    print("Ensuring GPS TPV table is setup properly")
    # Ref Table 1 from here: https://gpsd.gitlab.io/gpsd/gpsd_json.html
    # Most of these columns will not be used
    # Sample TPV message from our device:
    # { "class":  "TPV",
    #   "device": "/dev/ttyUSB0",
    #   "mode":    3,
    #   "time":   "2021-04-22T20:53:23.000Z",
    #   "ept":     0.005,
    #   "lat":     40.421641854,
    #   "lon":    -86.916256391,
    #   "alt":     200.172,
    #   "epx":     31.500,
    #   "epy":     23.863,
    #   "epv":     106.490,
    #   "track":   359.0756,
    #   "speed":   0.590,
    #   "climb":   0.002,
    #   "eps":     1.66,
    #   "epc":     212.98 }
    db.run("""
            CREATE TABLE IF NOT EXISTS gps_tpv (
              systime timestamptz UNIQUE NOT NULL,
              device text,
              mode smallint NOT NULL,
              status smallint,
              time timestamptz,
              altHAE double precision,
              altMSL double precision,
              alt double precision,
              climb double precision,
              datum text,
              depth double precision,
              dgpsAge double precision,
              dgpsSta double precision,
              epc double precision,
              epd double precision,
              eph double precision,
              eps double precision,
              ept double precision,
              epx double precision,
              epy double precision,
              epv double precision,
              geoidSep double precision,
              lat double precision,
              lon double precision,
              track double precision,
              magtrack double precision,
              magvar double precision,
              speed double precision,
              ecefx double precision,
              ecefy double precision,
              ecefz double precision,
              ecefpACC double precision,
              ecefvx double precision,
              ecefvy double precision,
              ecefvz double precision,
              ecefvACC double precision,
              sep double precision,
              relD double precision,
              relE double precision,
              relN double precision,
              wanglem double precision,
              wangler double precision,
              wanglet double precision,
              wspeedr double precision,
              wspeedt double precision);""")

    print("Ensuring GPS TPV table is a timescaledb hypertable")
    db.run("SELECT create_hypertable('gps_tpv', 'systime', if_not_exists => TRUE, migrate_data => TRUE);")

    # Create GPS SKY table
    print("Ensuring GPS SKY table is setup properly")
    # Ref Table 2 from here: https://gpsd.gitlab.io/gpsd/gpsd_json.html
    # Most of these columns will not be used
    # Sample SKY message from our device with truncated number of sats:
    # {
    #   "class": "SKY",
    #   "device": "/dev/ttyUSB0",
    #   "xdop": 0.9,
    #   "ydop": 0.96,
    #   "vdop": 2.18,
    #   "tdop": 1.13,
    #   "hdop": 1.31,
    #   "gdop": 2.76,
    #   "pdop": 2.54,
    #   "satellites": [
    #     { "PRN": 1,  "el": 26, "az": 281, "ss": 17, "used": false, "gnssid": 0, "svid": 1 },
    #     { "PRN": 3,  "el": 16, "az": 317, "ss": 0,  "used": false, "gnssid": 0, "svid": 3 },
    #     { "PRN": 10, "el": 27, "az": 150, "ss": 29, "used": true, "gnssid": 0, "svid": 10 }]}
    db.run("""
            CREATE TABLE IF NOT EXISTS gps_sky (
              systime timestamptz UNIQUE NOT NULL,
              device text,
              time timestamptz,
              gdop double precision,
              hdop double precision,
              pdop double precision,
              tdop double precision,
              vdop double precision,
              xdop double precision,
              ydop double precision,
              nSat double precision,
              uSat double precision,
              satellites json);""")


    print("Ensuring GPS SKY table is a timescaledb hypertable")
    db.run("SELECT create_hypertable('gps_sky', 'systime', if_not_exists => TRUE, migrate_data => TRUE);")

    # Create GPS PPS table
    # TODO: Double check these data types
    print("Ensuring GPS PPS table is setup properly")
    # Ref Table 8 from here: https://gpsd.gitlab.io/gpsd/gpsd_json.html
    # Most of these columns will not be used
    # Sample PPS message from our GPS module:
    # {
    #   "class": "PPS",
    #   "device": "/dev/ttyUSB3",
    #   "real_sec": 1603741751,
    #   "real_nsec": 0,
    #   "clock_sec": 1603741751,
    #   "clock_nsec": 8980399,
    #   "precision": -10
    # }
    db.run("""
            CREATE TABLE IF NOT EXISTS gps_pps (
              systime timestamptz UNIQUE NOT NULL,
              device text,
              real_sec bigint,
              real_nsec bigint,
              clock_sec bigint,
              clock_nsec bigint,
              precision int,
              qErr int);""")


    print("Ensuring GPS PPS table is a timescaledb hypertable")
    db.run("SELECT create_hypertable('gps_pps', 'systime', if_not_exists => TRUE, migrate_data => TRUE);")

    print("Finished setting up tables")



def connect_db():

    import postgres
    import os
    import sys
    from time import sleep
    from psycopg2 import OperationalError

    # Try to connect to the DB. It may be starting up so we should try a few timees
    # before failing. Currently trying every second 60 times
    tries = 0
    maxtries = 60
    sleeptime = 1
    db_connected = False
    connectionurl = 'postgresql://' + os.environ['db_user'] + ':' + os.environ['db_password'] + \
        '@postgres:' + os.environ['db_port'] + '/' + os.environ['db_database']
    while(not db_connected):
        try:
            print("Attempting connection to database")
            db = postgres.Postgres(url=connectionurl)
        except OperationalError as e:
            if(tries < maxtries):
                print("Database connection attempt", tries,
                      "failed. Database may still be starting. Sleeping", sleeptime, "s and trying again")
                print(e)
                tries = tries + 1
                sleep(sleeptime)
            else:
                print("FATAL: Could not connect to db after",
                      tries, "tries. Exiting")
                sys.exit(-1)
        else:
            print("Connection successful")
            db_connected = True
    
    setup_db_tables(db)
    sys.stdout.flush()

    return db

