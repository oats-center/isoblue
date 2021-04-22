#!/usr/bin/python3
import postgres
import os
import sys
from time import sleep
from psycopg2 import OperationalError
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers


def setup_db_tables(db):
    print("Ensuring timescaledb extension is activated")
    db.run("CREATE EXTENSION IF NOT EXISTS timescaledb;")

    # Create GPS tpv table
    print("Ensuring tables are setup properly")
    # Ref Table 1 from here: https://gpsd.gitlab.io/gpsd/gpsd_json.html
    # Most of these columns will not be used
    # Sample TPV message from out device:
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
            CREATE TABLE IF NOT EXISTS gps.tpv (
              device text
              mode smallint NOT NULL
              status smallint
              time timestamptz UNIQUE NOT NULL,
              altHAE double precision
              altMSL double precision
              alt double precision
              climb double precision
              datum text
              depth double precision
              dgpsAge double precision
              dgpsSta dobule precision
              epc double precision
              epd double precision
              eph double precision
              eps double precision
              ept double precision
              epx double precision
              epy double precision
              epv double precision
              geoidSep double precision
              lat double precision
              lon double precision
              track double precision
              magtrack double precision
              magvar double precision
              speed double precision
              ecefx double precision
              ecefy double precision
              ecefz double precision
              ecefpACC double precision
              ecefvx double precision
              ecefvy double precision
              ecefvz double precision
              ecefvACC double precision
              sep double precision
              relD double precision
              relE double precision
              relN double precision
              wanglem double precision
              wangler double precision
              wanglet double precision
              wspeedr double precision
              wspeedt double precision);""")
    print("Ensuring GPS point table is a timescaledb hypertable")
    db.run("SELECT create_hypertable('gps.tpv', 'time', if_not_exists => TRUE, migrate_data => TRUE);")
    print("Finished settting up tables")



def connect_db():
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


async def run(loop):
    print("Setting up NATS")
    sys.stdout.flush()
    nc = NATS()

    print("Connecting to nats server")
    await nc.connect("nats://nats:4222")

    print("Connecting to database")
    db = connect_db()

    print("Setting up db")
    setup_db_tables(db) 

    async def notify_tpv(msg):

        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        tpv_fix  = json.loads(data)
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

        # build sql query from json
        if "time" in tpv_fix:
            print("Inserting for timestamp", gps_tpv["time"])
            db.run("INSERT INTO gps.tpv select (json_populate_record(null:gps.tpv,
                   '%s'::json)).*;", data)
        else:
          print("GPS point had no timestamp, could not insert into time-series database")
        sys.stdout.flush()


    notify_subject = 'gps.tpv' 
    print("Subscribing to subject", notify_subject)
    await nc.subscribe(notify_subject, cb=notify_tpv)

    while True:
      await asyncio.sleep(1)

    # Gracefully close the connection.
    await nc.drain()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
