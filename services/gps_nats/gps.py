#!/usr/bin/python3
import os
import asyncio
import nats
import json
import ast
from gpsdclient import GPSDClient

print("Starting gps_nats...")

async def main():


    # Create nats object and connect to local nats server
    print('Connecting to NATS server')
    nc = await nats.connect("nats://localhost:4222")
    # Get list of GPSD classes to send over NATS
    gpsd_classes = "[" + os.getenv('GPSD_CLASSES') + "]"
    # Use AST to parse the classes string into a list
    try:
        gpsd_classes = ast.literal_eval(gpsd_classes)
    except:
        print("Failed to parse GPSD_CLASSES env. variable. Defaulting to all classes")
        gpsd_classes=None

    with GPSDClient(host="127.0.0.1") as client:
        for result in client.dict_stream(filter=gpsd_classes)
        # Parse incoming GPSD JSON strings
        try:
            fix = json.loads(results)
        except:
            # Ignore string if unable to parse
            print("Failed to parse JSON message")
        subject = os.getenv('AVENA_PREFIX') + ".gps." + str(fix["class"])
        #print("Publishing new data point to subject", subject, ": ", new_data[:-1])
        await nc.publish(subject, bytes(new_data, 'utf-8'))
    # Loop runs out of control without this
    #sleep(0.001)

if __name__ == '__main__':

    try:
        asyncio.run(main())
    finally:
        print("Stopping gps_nats...")

    sys.exit(0)
