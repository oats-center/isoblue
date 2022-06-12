#!/usr/bin/python3
import os
from prometheus_client import start_http_server, Gauge
import sys
from time import sleep
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
import json
from gps3 import gps3

sleep(5)
print("Starting GPS_NATS")
sys.stdout.flush()

async def run(loop):
    # Prometheus variables to export
    global lat_gauge
    lat_gauge = Gauge('avena_position_lat', 'Last know fix latitude')
    global lng_gauge
    lng_gauge = Gauge('avena_position_lng', 'Last know fix longitude')
    global time_gauge
    time_gauge = Gauge('avena_position_time', 'Last know fix time')
    #start_http_server(10001)

    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    #gps_socket.connect(host='127.0.0.1', port=2948)
    gps_socket.connect(host='127.0.0.1', port=2947)
    gps_socket.watch()

    # Create nats object and connect to local nats server
    print('Setting up NATS')
    sys.stdout.flush()
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    #await nc.connect("nats://nats:4222")

    for new_data in gps_socket:
        if new_data:
            fix = json.loads(new_data)
            subject = os.getenv('HOSTNAME') + ".gps." + str(fix["class"])
            print("Publishing new data point to subject", subject, ": ", new_data[:-1])
            await nc.publish(subject, bytes(new_data, 'utf-8'))
            await nc.flush(1)

            if "activated" in fix and fix["activated"] == 0:
                await nc.flush(10)
                print("NC flushed")
            sys.stdout.flush()
        # Loop runs out of control without this
        sleep(0.1)

    print("This should never be reached")
            

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()

    sys.exit(0)
