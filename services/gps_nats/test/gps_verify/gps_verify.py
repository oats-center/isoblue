#!/usr/bin/python3
import time
import os
import sys
import json
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers


async def run(loop):

    print('Setting up NATS')
    # Connect to NATS server
    nc = NATS()
    await nc.connect('nats://nats:4222')

    # Notifies the non-callback function that we are finished
    # Yeah I know it's not pythonic. Open a PR smart guy
    fin = asyncio.Future()

    testpoints_file = open('/opt/test_points/test_points.log', 'r')

    async def message_handler(msg):
        nats_gps_point = msg.data.decode()
        file_gps_point = testpoints_file.readline()

        while not 'class":"TPV"' in file_gps_point:
          print("skipping", file_gps_point)
          file_gps_point = testpoints_file.readline()

        # Debugging
        print('Recieved on subject:',msg.subject)
        print('NATS type:', type(nats_gps_point), '\nmessage:', nats_gps_point)
        print('line type:', type(file_gps_point), '\nmessage:', file_gps_point) 

        '''
        if nats_gps_point == 'END':
            print('End control message received. No more gps points to check')
            fin.set_result(message_handler.points_received)
            return

        # Check for NAT's point
        print('Verifying that nats',
              nats_gps_point['time'], ' is in the database')

        # Counter just for fun
        if not hasattr(message_handler, 'points_received'):
            message_handler.points_received = 0  # it doesn't exist yet, so initialize it
        message_handler.points_received = message_handler.points_received + 1
        '''
        sys.stdout.flush()
        return

    print('setting up gps message callback')
    sid = await nc.subscribe('gps.TPV', cb=message_handler)
    print('gps message callback setup')
    sys.stdout.flush()

    await fin
    # If fin is a positive number, the test was successful and the number is the number of points
    # verified. If it is negative, the test failed
    if fin.result() > 0:
        print('End message received. Exiting')
        print('Successfully verified %d points' % fin.result())
    else:
        print('Test failed')
    await nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()

    sys.exit(0)
