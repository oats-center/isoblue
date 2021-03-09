#!/usr/bin/python3
import os
from prometheus_client import start_http_server, Gauge
import sys
from time import sleep
import gpsd
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
import json

print("Starting GPS_NATS")
sys.stdout.flush()

sleep(2)

async def run(loop):
    # Prometheus variables to export
    global lat_gauge
    lat_gauge = Gauge('avena_position_lat', 'Last know fix latitude')
    global lng_gauge
    lng_gauge = Gauge('avena_position_lng', 'Last know fix longitude')
    global time_gauge
    time_gauge = Gauge('avena_position_time', 'Last know fix time')
    start_http_server(10001)

    #addr = '172.17.0.1'
    #addr = 'host.docker.internal'
    addr= 'localhost'
    port = 2947
    print("Connecting to gpsd at", addr, ":", port )
    sys.stdout.flush()

    gpsd.connect(host=addr, port=port)

    # Create nats object and connect to local nats server
    print('Setting up NATS')
    sys.stdout.flush()
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    while True: 
        packet = gpsd.get_current()
        if packet.mode >= 2:
            print("Time:", packet.time, "lat:", packet.lat, "lng:", packet.lon)
            lat_gauge.set(packet.lat)
            lng_gauge.set(packet.lon)
            #time_gauge.set(packet.time)
            await nc.publish("gps", json.dumps(packet).encode())

        else:
            print("GPS fix is only in mode", packet.mode, ", no location fix available")
        sys.stdout.flush()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()

    sys.exit(0)
