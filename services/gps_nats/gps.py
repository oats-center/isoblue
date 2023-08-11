#!/usr/bin/python3
import os
import asyncio
import nats
import json
from gpsdclient import GPSDClient

print("Starting gps_nats...")

async def main():


    # Create nats object and connect to local nats server
    print('Connecting to NATS server...')
    try:
        nc = await nats.connect("nats://localhost:4222")
        print("NATS connection successful!")
    except:
        print("Failed to connect to NATS server")
    # Get list of GPSD classes to send over NATS
    gpsd_classes = os.getenv('GPSD_CLASSES').split(',')
    
    # Read from GPSD socket
    with GPSDClient(host="127.0.0.1") as client:
        for result in client.json_stream(filter=gpsd_classes):
            # Parse incoming GPSD JSON strings
            try:
                msg = json.loads(result)
            except:
            # Ignore string if unable to parse
                print("Failed to parse JSON message")
                continue
            subject = f"{os.getenv('AVENA_PREFIX')}.gps.{msg['class']}"
            # Publish received JSON message
            await nc.publish(subject, bytes(result, 'utf-8'))
            await asyncio.sleep(0.001)

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
        
    try:
        loop.run_forever()
    except(KeyboardInterrupt):
        print("Stopping gps_nats...")
        quit()
    loop.close()

