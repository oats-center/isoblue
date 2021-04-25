#!/usr/bin/python3
import postgres
import os
import sys
from time import sleep
import json
from psycopg2 import OperationalError
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from manage_db import setup_db_tables, connect_db 

async def run(loop):
    print("Setting up NATS")
    sys.stdout.flush()
    nc = NATS()

    print("Connecting to nats server")
    #await nc.connect("nats://localhost:4222")
    await nc.connect("nats://nats:4222")

    print("Connecting to database")
    db = connect_db()

    print("Setting up db")
    setup_db_tables(db) 

    async def notify_tpv(msg):

        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        fix  = json.loads(data)
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))
        sys.stdout.flush()

        # build sql query from json
        if "time" in fix:
            print("Inserting for timestamp", fix["time"])
            db.run("INSERT INTO gps_tpv select (json_populate_record(null::gps_tpv,%s::json)).*;", (data, ))
        else:
          print("GPS TPV point had no timestamp, could not insert into time-series database")
        sys.stdout.flush()

    async def notify_sky(msg):

        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        fix  = json.loads(data)
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))
        sys.stdout.flush()

        # build sql query from json
        if "time" in fix:
            print("Inserting for timestamp", fix["time"])
            db.run("INSERT INTO gps_sky select (json_populate_record(null::gps_sky,%s::json)).*;", (data, ))
        else:
          print("GPS SKY point had no timestamp, could not insert into time-series database")
        sys.stdout.flush()

    async def notify_pps(msg):

        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        fix  = json.loads(data)
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))
        sys.stdout.flush()

        # build sql query from json. Don't need to check for time as clock_sec is required for gpsd spec
        print("Inserting for timestamp", fix["clock_sec"])
        db.run("INSERT INTO gps_pps select (json_populate_record(null::gps_pps,%s::json)).*;", (data, ))
        sys.stdout.flush()

    notify_subject = 'gps.TPV' 
    print("Subscribing to subject", notify_subject)
    await nc.subscribe(notify_subject, cb=notify_tpv)

    notify_subject = 'gps.SKY' 
    print("Subscribing to subject", notify_subject)
    await nc.subscribe(notify_subject, cb=notify_sky)

    notify_subject = 'gps.PPS' 
    print("Subscribing to subject", notify_subject)
    await nc.subscribe(notify_subject, cb=notify_pps)

    while True:
      await asyncio.sleep(1)

    # Gracefully close the connection.
    await nc.drain()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
