#!/usr/bin/python3
import os
import sys
from time import sleep
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from twilio.rest import Client

async def run(loop):
    print("Setting up NATS")
    sys.stdout.flush()
    nc = NATS()

    print("Connecting to nats server")
    await nc.connect("nats://nats:4222")

    account_number = os.environ['TWILIO_ACCT_NUMBER']
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    dest_number = os.environ['DEST_NUMBER']
    client = Client(account_sid, auth_token)
    print("Using phone number", account_number, "to send to phone number", dest_number)


    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))
        if int(data) > 9:
            print("Recieved message is in the double digits. Sending notification")
            message = client.messages \
                            .create(
                                 body="The number got above double digits! Number: " + data,
                                 from_=account_number,
                                 to=dest_number
                 )

            print(message.sid)
        sys.stdout.flush()


    subject = 'sms' 
    print("Subscribing to subject", subject)
    await nc.subscribe(subject, cb=message_handler)

    while True:
      await asyncio.sleep(1)

    # Gracefully close the connection.
    await nc.drain()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
