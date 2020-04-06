#!/usr/bin/env python

import io
import os
import sys
import json
import avro
import avro.schema
import avro.io

from gps3 import gps3
from kafka import KafkaProducer
from time import sleep
from datetime import datetime

schema_path = './gps.avsc'

if __name__ == "__main__":

    # valid environment variables
    if 'kafka_topic' in os.environ:
        pass
    else:
        sys.exit('Kafka topic not given. Exiting ...')

    # create kafka producer
    producer = KafkaProducer(bootstrap_servers=['kafka:9092'])
    # exit if not connected to Kafka broker
    if producer.bootstrap_connected():
        print('Connected to Kafka broker')
    else:
        sys.exit('Cannot connect to Kafka broker. Exiting ...')

    # load avro schema
    f = open(schema_path).read()
    try:
        sch = avro.schema.parse(f)
    except Exception as e:
        print(e)
        sys.exit()

    # set up gpsd socket
    s = gps3.GPSDSocket()
    s.connect(host='host.docker.internal', port=2947) #FIXME
    s.watch()

    timestamp = None
    last_tpv_timestamp = None

    try:
        for data in s:
            if data:
                new_data = json.loads(data)
                object_name = new_data.pop('class', 'ERROR')

                # convert 'n/a' to None for proper
                for key, value in new_data.items():
                    if value == 'n/a':
                        new_data[key] = None

                # the object should be TPV now #FIXME: can only handle TPV
                if object_name == 'TPV':
                    if 'time' in new_data:
                        utc_dt = datetime.strptime(new_data['time'], \
                                                   '%Y-%m-%dT%H:%M:%S.%fZ')
                        timestamp = int((utc_dt - \
                                         datetime(1970, 1, 1)).total_seconds())
                        new_data['time'] = timestamp

                    last_tpv_timestamp = timestamp
                # ditch other samples
                else:
                    continue

                # create datum
                d = {}
                d = new_data
                if object_name == 'SKY':
                    d['time'] = last_tpv_timestamp

                writer = avro.io.DatumWriter(sch)
                bytes_writer = io.BytesIO()
                encoder = avro.io.BinaryEncoder(bytes_writer)

                # write to the datum
                writer.write(d, encoder)
                # produce the message to Kafka
                gps_msg = bytes_writer.getvalue()
                producer.send(os.environ['kafka_topic'], \
                              value=gps_msg)

                d = {}
                gps_d = None

            sleep(0.1)

    except KeyboardInterrupt:
        s.close()
