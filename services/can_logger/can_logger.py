#!/usr/bin/env python3

import socket
import postgres
import csv
import os

def write_to_csv(timestamp, can_id, can_data, host_interface):


    with open('/data/log/' + host_interface + '.csv', mode = 'a') as log:

        log = csv.writer(log, delimiter = ',', quotechar = '"',
                         quoting = csv.QUOTE_MINIMAL)

        log.writerow([timestamp, can_id, can_data])

def write_to_db(timestamp, can_id, can_data):

    db.run("INSERT INTO cell (time, can_id, can_data) VALUES (to_timestamp(%s), \
            %s, %s)", (timestamp, can_id, can_data))

    print("Finished inserting CAN bus data for timestamp ", timestamp)

def db_init():
    
    global db

    connection_url = ('postgresql://' + os.environ['db_user'] + ':' + 
                 os.environ['db_password'] + '@postgres:' + 
                 os.environ['db_port'] + '/' + os.environ['db_database'] )

    print('Initializing Postgres Object...')
    db = postgres.Postgres(url = connection_url)

    print('Ensuring timescaledb ext. is enabled')
    db.run("CREATE EXTENSION IF NOT EXISTS timescaledb;")
    print("Ensuring tables are setup properly")
    db.run("""
           CREATE TABLE IF NOT EXISTS cell (
               time timestamptz UNIQUE NOT NULL,
               can_id text NOT NULL,
               can_data text NOT NULL);""")

    print("Ensuring cell data table is a timescaledb hypertable")
    db.run("""
           SELECT create_hypertable('cell', 'time', if_not_exists => TRUE,  
           migrate_data => TRUE);""")

    print("Finished setting up tables")


#Get host info using environment variables

host_ip = os.environ['socketcand_ip']
host_port = os.environ['socketcand_port']
host_interface = os.environ['can_interface']
logging = os.environ['log']

#Initialize postgres database if database logging is enabled

if(logging.find('db') != -1):
    
    db_init()

#Initialize host socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host_ip, host_port))

print (s.recv(32))

#Connect to exposed CAN interface

s.sendall(b'< open ' + host_interface.encode('utf-8') + b' >')

print (s.recv(32))

s.sendall(b'< rawmode >')

print(s.recv(32))

while(True):
    
    frame = s.recv(128).decode("utf-8").strip("<>''").split(' ')
    [timestamp, can_id, can_data] = (frame[3], frame[2], frame[4])
    
    if(logging.find('db') != -1):
        
        write_to_db(timestamp, can_id, can_data)
    
    else:
        
        write_to_csv(timestamp, can_id, can_data, host_interface)
