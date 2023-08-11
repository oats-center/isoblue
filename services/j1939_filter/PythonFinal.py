import asyncio
import nats
import json
import time


async def main():
    # Connect to NATS!
    nc = await nats.connect("localhost")  # change ip to connect to correct isoblue

    sub = await nc.subscribe("j1939.data.>") # .raw is raw from can bus| .data is decoded data | .filter is filtered data
    
    async def keys_request(msg):
        print("Request Recieved")	
        await nc.publish(msg.reply, bytes(json.dumps(list(subjects.keys())), 'utf-8'))

    reqSub = await nc.subscribe("j1939.keys", "workers", keys_request)
            # Process the message
    subjects = {}
    msg = await sub.next_msg()   #waits for next message
    

    try:  
        
        async for msg in sub.messages:
            messageStr = msg.data.decode()  #decodes the data 
            message = json.loads(messageStr)   # turns the data into a json dictionary
            filterSubject = msg.subject   # takes the subject 
            if message["value"] < message["max_value"] and message["value"] != "null":
        
            
                filterSubject = "j1939.filter." + message["name"]
                if subjects.get(filterSubject) == None: 

                   subjects[filterSubject] = { 
                                           "sumVal": 0, 
                                            "number": 0,
                                            "average": 0,
                                            "sumOfSquares": 0,
                                            "max_value": message["max_value"],
                                            "min_value": message["min_value"],
                                            "name": message["name"],
                                            "pgn": message["pgn"],
                                            "units": message["units"],
                                            "from": 0,
                                            "to": 0,
                                            "lastSent": time.time()
                                            }
                   
                   
                t = subjects.get(filterSubject)

                t["sumVal"] = float(t["sumVal"])
                t["sumVal"] += message["value"]
                t["sumOfSquares"] = float(t["sumOfSquares"])
                t["sumOfSquares"] += (message["value"])**2
                
                if subjects[filterSubject]["number"] == 0:
                    subjects[filterSubject]["from"] = time.time()

                                
                else:
                    subjects[filterSubject]["to"] = time.time()
                
                subjects[filterSubject]["number"] = float(subjects[filterSubject]["number"])
                subjects[filterSubject]["number"] += 1 
                
                
                if subjects[filterSubject]["lastSent"] + 1 <= time.time():
                
                    subjects[filterSubject]["average"] = subjects[filterSubject]["sumVal"]/t["number"]
                    subjects[filterSubject]["lastSent"] = time.time()
                    await nc.publish(filterSubject, bytes(json.dumps(subjects[filterSubject]), 'utf-8'))
                    subjects[filterSubject]["sumVal"] = "0"
                    subjects[filterSubject]["number"] = "0"
                    subjects[filterSubject]["sumOfSquares"] = "0"
                
             
       
    except Exception as e:
       print(e)
    finally:
       print("closing loop")
       loop.close()

loop = asyncio.new_event_loop()
try:

    asyncio.run(main())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("closing loop. Boiler Up!")
    loop.close()
