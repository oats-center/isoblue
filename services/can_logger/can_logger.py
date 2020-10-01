#!/usr/bin/env python3

import socket
import postgres
import csv
import os

def csv_init(host_interface):
    # Open the log file
    logfd = open('/data/log/' + host_interface + '.csv', mode = 'a') 
    # Make csv writer object using log file
    logcsv = csv.writer(log, delimiter = ',', quotechar = '"',
                         quoting = csv.QUOTE_MINIMAL)
    return logcsv

def write_to_csv(timestamp, can_id, can_data, log):
        log.writerow([timestamp, can_id, can_data])

def write_to_db(rx_buff, db):

    db.run("INSERT INTO can (time, can_id, can_data) VALUES (%s)", (rx_buff))

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

# Initialize received frame buffer

rx_buf = []

logtodb = False
logtocsv = False
if logging.find('db') != -1:
    logtodb = True
if logging.find('csv') != -1:
    logtocsv = True

# Initialize postgres database if database logging is enabled
if logtodb:
    db = db_init()

# Initialize CSV file if CSV logging is enabled
if logtocsv:
    csv_log = csv_init()

# Initialize host socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host_ip, host_port))

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

        if(logging.find('db') != -1):
        
            # TODO: Write to database in a separate thread/process.
            wr_buff = rx_buff.copy()
            write_to_db(wr_buff)
    
    if(logging.find('csv') != -1):
        
        write_to_csv(timestamp, can_id, can_data, csv_log)
