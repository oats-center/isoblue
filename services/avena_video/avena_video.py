#!/usr/bin/python3

import asyncio
import nats
import os
import json
from functools import partial
from datetime import datetime
from ffmpeg import Progress, FFmpegError
from ffmpeg.asyncio import FFmpeg

async def main():
    
    print(f"Starting Avena RTSP video stream on {os.getenv('AVENA_PREFIX')} with {os.getenv('CAMERA')} camera")
    ## Connect to NATS server running in localhost
    nc = await nats.connect("nats://localhost:4222")
    
    rtsp_url = f"rtsp://{os.getenv('RTSP_USER')}:{os.getenv('RTSP_PASSWORD')}@@{os.getenv('CAMERA_IP')}:{os.getenv('RTSP_PORT')}/s1"
    rtp_url = f"rtp://{os.getenv('RTP_ENDPOINT')}:{os.getenv('RTP_PORT')}/{os.getenv('AVENA_PREFIX')}-{os.getenv('CAMERA')}"
    
    ## Specify ffmpeg options to convert an RTSP stream to a RTP stream
    stream = (
        FFmpeg()
        .option("copyts")
        .option("fflags", value="nobuffer")
        #.option("vcodec", value="copy")
        .option("movflags", value="frag_keyframe+empty_moov")
        .input(rtsp_url, rtsp_transport="tcp")
        .output(rtp_url)
    )

    ## Print initialization messages
    @stream.on("start")
    def on_start(arguments: list[str]):
        print("Starting FFmpeg...")

    ## Print error messages
    @stream.on("stderr")
    def on_stderr(line):
        print(line)

    ## Print current progress
    @stream.on("progress")
    def on_progress(progress: Progress):
        print(progress)

    @stream.on("terminated")
    def on_terminated():
        print(f"FFmpeg terminated succesfully")

    ## Toggle RTSP stream via req-reply NATS messages
    async def toggle_stream(stream, msg):

        reply = {}
        request = json.loads(msg.data.decode())
        cmd = request['command']

        reply["time"] = datetime.now().isoformat()
        reply["command"] = cmd
        reply["camera"] = os.getenv('CAMERA')

        if cmd == "start":
    
            ## Start FFmpeg with the options above

            try:
                #asyncio.create_task(stream.execute(), name="video-stream")
                task = asyncio.gather(stream.execute(), return_exceptions=False)
            ## FIX-ME: Handle error appropriately. Exceptions from future are not being
            ## handled
            except(FFmpegError):
                print(f"Failed to start {os.getenv('CAMERA')} video stream")
                reply["status"] = "fail"
            
            
            reply["status"] = "ok"

        elif cmd == "stop":
            
            print("Stopping video stream...")
            try:
                stream.terminate()
                reply["status"] = "ok"

            except(FFmpegError):
                print("No stream to stop. Doing nothing...")
                reply["status"] = "fail"

        else:
            reply["status"] = "fail"
            print('Invalid command received. Doing nothing...')
        
        reply = json.dumps(reply)
        await nc.publish(msg.reply, bytes(reply, "utf-8"))

    # Use queue named 'stream' for distributing requests
    # among subscribers.
    subject = f"{os.getenv('AVENA_PREFIX')}.video.{os.getenv('CAMERA')}.control" 
    sub = await nc.subscribe(subject=subject, queue="stream", cb=partial(toggle_stream, stream))
    

if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    try:
        loop.run_forever()
    except(KeyboardInterrupt):
        print("Ctrl+C detected. Terminating...")
        quit()
    loop.close()

