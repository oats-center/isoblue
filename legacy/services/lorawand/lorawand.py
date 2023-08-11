import asyncio

from serial_asyncio import open_serial_connection
from nats.aio.client import Client as NATS # type: ignore

q: asyncio.Queue = asyncio.Queue()

async def ser():
    reader, writer = await open_serial_connection(url='/dev/ttyXRUSB0', baudrate=115200)
    print('hello from serial')
    return reader, writer

async def process_queue():
    ser_r, ser_w = await ser()
    while True:
        msg = await q.get()

        if msg['type'] == 'config':
            print('[config] Set echo off')
            await asyncio.sleep(1)
            ser_w.write('ATE0\r\n'.encode())
            ser_w.write('AT\r\n'.encode())
            r = await ser_r.readline()
            await msg['q'].put(r)

        if msg['type'] == 'send':
            print('[send] Sending')
            await asyncio.sleep(1)
            ser_w.write('AT\r\n'.encode())
            print('[send] Sent')

            r = await ser_r.readline()
            await msg['q'].put(r)

async def nat():
    nc = NATS()
    await nc.connect('demo.nats.io:4222')

    print('hello from nats')

    async def process_config(msg):
        res: asyncio.Queue = asyncio.Queue()
        await q.put({'type': 'config', 'q': res})
        r = await res.get()
        await nc.publish(msg.reply, r)

    async def process_send(msg):
        res: asyncio.Queue = asyncio.Queue()
        await q.put({'type': 'send', 'q': res})
        r = await res.get()
        await nc.publish(msg.reply, r)

    await nc.subscribe('isoblue.lorawand.config', cb=process_config)
    await nc.subscribe('isoblue.lorawand.send', cb=process_send)

async def run():
    await nat()
    await process_queue()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
