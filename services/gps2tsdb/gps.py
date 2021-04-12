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
    print("Ensuring tables are setup properly")
    db.run("""
            CREATE TABLE IF NOT EXISTS gps (
              time timestamptz UNIQUE NOT NULL,
              lat double precision NOT NULL,
              lng double precision NOT NULL);""")
    print("Ensuring GPS point table is a timescaledb hypertable")
    db.run("SELECT create_hypertable('gps', 'time', if_not_exists => TRUE, migrate_data => TRUE);")
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



    async def notify_sms(msg):

        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

        sys.stdout.flush()


    async def new_subscriber(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    notify_subject = 'sms' 
    print("Subscribing to subject", notify_subject)
    await nc.subscribe(notify_subject, cb=notify_sms)

    subscribe_subject = "isoblue.notifications.sms.new_subscriber"
    print("Subscribing to subject", subscribe_subject)
    await nc.subscribe(subscribe_subject, cb=new_subscriber)

    while True:
      await asyncio.sleep(1)

    # Gracefully close the connection.
    await nc.drain()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
