#!/usr/bin/env python

import os
import io
import json
import sys
import re
import struct

import avro.schema
import avro.io

import paho.mqtt.client as mqtt

from kafka import KafkaConsumer
from struct import *

# ISOBUS message masks
MASK_2_BIT = ((1 << 2) - 1)
MASK_3_BIT = ((1 << 3) - 1)
MASK_8_BIT = ((1 << 8) - 1)

# avro schema path
schema_path = './raw-can.avsc'

# isobus message parser
def parse(hex_message, timestamp=0):
    # J1939 header info:
    # http://www.ni.com/example/31215/en/
    # http://tucrrc.utulsa.edu/J1939_files/HeaderStructure.jpg
    header_hex = hex_message[:8]
    header = int(header_hex, 16)

    sa = header & MASK_8_BIT
    header >>= 8
    pdu_ps = header & MASK_8_BIT
    header >>= 8
    pdu_pf = header & MASK_8_BIT
    header >>= 8
    res_dp = header & MASK_2_BIT
    header >>= 2
    priority = header & MASK_3_BIT

    pgn = res_dp
    pgn <<= 8
    pgn |= pdu_pf
    pgn <<= 8
    if pdu_pf >= 240:
        # pdu format 2 - broadcast message. PDU PS is an extension of
        # the identifier
        pgn |= pdu_ps
        da = 255
    else:
        da = pdu_ps

    payload_bytes = re.findall('[0-9a-fA-F]{2}', hex_message[8:])
    payload_int = int(''.join(reversed(payload_bytes)), 16)

    return {'pgn': pgn,
            'sa': sa,
            'da': da,
            'priority': priority,
            'payload_int': payload_int,
            'payload_bytes': payload_bytes,
            'header': header_hex,
            'message': hex_message,
            'timestamp': timestamp}

def on_connect(client, userdata, flags, rc):
    print('Connected to remote MQTT broker!')

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Disconnected from remote MQTT broker, reconnecting ...')
        client.reconnect()

if __name__ == '__main__':

    # valid environment variables
    if 'kafka_topic' in os.environ:
        pass
    else:
        sys.exit('Kafka topic not given. Exiting ...')

    if 'isoblue_id' in os.environ:
        pass
    else:
        sys.exit('ISOBlue id not given. Exiting ...')

    if 'cloud_domain' in os.environ:
        pass
    else:
        sys.exit('Cloud domain not given. Exiting ...')

    if 'mqtt_topic' in os.environ:
        pass
    else:
        sys.exit('MQTT topic not given. Exiting ...')

    if 'mqtt_port' in os.environ:
        pass
    else:
        sys.exit('MQTT port not given. Exiting ...')

    # initialize consumer
    consumer = KafkaConsumer(os.environ['kafka_topic'], \
                             bootstrap_servers='kafka:9092', \
                             client_id='engine-rpm-consumer')

    if consumer.bootstrap_connected():
        print('Connected to Kafka broker')
    else:
        sys.exit('Cannot connect to Kafka broker. Exiting ...')

    # load avro schema
    schema = avro.schema.parse(open(schema_path).read())

    # connect to remote mqtt broker
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.username_pw_set(os.environ['isoblue_id'], '')
    client.connect(os.environ['cloud_domain'], int(os.environ['mqtt_port']))
    client.loop_start()

    try:
        # read from Kafka logs
        for msg in consumer:
            print(msg.key.decode('utf-8'))
            keys = msg.key.decode('utf-8').split(':')
            if keys[0] != os.environ['kafka_topic']:
                sys.exit('Key error. Exiting ...')

            # skip any message that does not have this PGN
            if keys[1] != '61444':
                continue

            # parse CAN frames
            # setup decoder
            bio = io.BytesIO(msg.value)
            decoder = avro.io.BinaryDecoder(bio)
            reader = avro.io.DatumReader(schema)
            r = reader.read(decoder)

            # unpack the binary data and convert it to a list
            d = struct.unpack('BBBBBBBB', r['payload'])
            d_list = list(d)

            # convert arbitration_id to hex, pad 0 to make it length 8
            arb_id = (hex(r['arbitration_id'])[2:]).rjust(8, '0')

            # iterate through data_list and pad 0 if the length is not 2
            for i in range(len(d_list)):
                # convert each number to hex string
                d_list[i] = hex(d_list[i])[2:]
                # pad zero if the hex number length is 1
                if len(d_list[i]) == 1:
                   d_list[i] = d_list[i].rjust(2, '0')

            # join hex string into one, make the message hex string
            d_payload = ''.join(d_list)
            msg = arb_id + d_payload
            msg_p = parse(msg, r['timestamp'])

            # only publish necessary message
            rpm_hex = d_payload[8:10] + d_payload[6:8]
            _d = {
                'ts': r['timestamp'],
                'rpm': int(rpm_hex, 16) * 0.125
            }
            print(_d)

            client.publish(os.environ['mqtt_topic'], \
                           payload=json.dumps(_d), qos=0)
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
