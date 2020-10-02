#!/usr/bin/env python3

import socket
import postgres
import csv
import os
import multiprocessing as mp

def csv_init(host_interface):
    
    # Open the log file
    
    logfd = open('/data/log/' + host_interface + '.csv', mode = 'a') 
    
    # Make csv writer object using log file
    
    logcsv = csv.writer(logfd, delimiter = ',', quotechar = '"',
                        quoting = csv.QUOTE_MINIMAL)
    
    return logcsv

def write_to_csv(log, wr_buff):
    
    # Write to CSV from write buffer. First item is timestamp, second is
    # can_id and third is can_data

    for row in wr_buff:
    
        log.writerow(row[0], row[1], row[2])

def write_to_db(db, wr_buff):

    db.run("INSERT INTO can (time, can_id, can_data) VALUES (%s)", (wr_buff))

def db_init():
    
    connection_url = ('postgresql://' + os.environ['db_user'] + ':' + 
                 os.environ['db_password'] + '@postgres:' + 
                 os.environ['db_port'] + '/' + os.environ['db_database'] )

    print('Initializing Postgres Object...')
    db = postgres.Postgres(url = connection_url)

    print('Ensuring timescaledb ext. is enabled')
    db.run("CREATE EXTENSION IF NOT EXISTS timescaledb;")
    print("Ensuring tables are setup properly")
    db.run("""
           CREATE TABLE IF NOT EXISTS can (
               time timestamptz UNIQUE NOT NULL,
               can_id text NOT NULL,
               can_data text NOT NULL);""")

    print("Ensuring can data table is a timescaledb hypertable")
    db.run("""
           SELECT create_hypertable('can', 'time', if_not_exists => TRUE,  
           migrate_data => TRUE);""")

    print("Finished setting up tables")

    return db

# Get host info using environment variables

host_ip = os.environ['socketcand_ip']
host_port = os.environ['socketcand_port']
host_interface = os.environ['can_interface']
logging = os.environ['log']

# Initialize received and write frame buffers and log selection variables

rx_buf = []
wr_buf = []
logtodb = False
logtocsv = False

# Check log selection from env. variables

if (logging.find('db') != -1):
    
    logtodb = True

if (logging.find('csv') != -1):
    
    logtocsv = True

# Initialize postgres database if database logging is enabled

if (logtodb):
    
    db = db_init()

# Initialize CSV file if CSV logging is enabled

if (logtocsv):

    csv_log = csv_init("can0")

# Initialize host socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host_ip, int(host_port)))

print (s.recv(32))

# Connect to exposed CAN interface

s.sendall(b'< open ' + host_interface.encode('utf-8') + b' >')

# DEBUG: Print socketcand's answer to the sent request

print (s.recv(32))

# Set socket to 'rawmode' to receive every frame on the bus.

s.sendall(b'< rawmode >')

print(s.recv(32))

# Receive frames in a 32-byte buffer and then decode the bytes object. Then
# strip some characters to clean up the received frame and then split the 
# resulting string to get the timestamp, CAN ID and CAN frame. 

while(True):
    
    frame = s.recv(32).decode("utf-8").strip("<>''").split(' ')

    (timestamp, can_id, can_data) = (frame[3], frame[2], frame[4])

    rx_buff.append((timestamp, can_id, can_data)) 
    
    # When the receive buffer reaches 100 entries, copy data from receive 
    # buffer to write buffer, then write to database from write buffer and
    # clear receive buffer to continue receiving data

    if(len(rx_buff) == 100):
        
        wr_buff.clear()
        wr_buff = rx_buff.copy()
        rx_buff.clear()

        if(logtodb):
 
            p_db = mp.Process(target=write_to_db, args=(db, wr_buff,))
            p_db.start()
    
        if(logtocsv):
        
            p_csv = mp.Process(target=write_to_csv, args=(csv_log, wr_buff,))
            p_csv.start()

