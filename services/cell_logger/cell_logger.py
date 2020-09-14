#!/usr/bin/env python3

import dbus
import time
import csv
import postgres
import os

#Query modem data using the ModemManager DBus object

def get_modem_rssi():

    modem_signal_iface = 'org.freedesktop.ModemManager1.Modem.Signal'

    modem_manager_object = bus.get_object('org.freedesktop.ModemManager1', 
                                          '/org/freedesktop/ModemManager1')
    modem_manager_iface = dbus.Interface(modem_manager_object, 
                                         'org.freedesktop.DBus.ObjectManager')

    modem_data = modem_manager_iface.GetManagedObjects()

#Extract modem path from the DBus data dictionary

    modem_path = list(modem_data.keys())[0]    

#Check if the 'Lte' dictionary has signal values assigned. If no values are
#found, assume the modem is connected via 'Umts'

    if(list(modem_data[dbus.ObjectPath(modem_path)][
                       dbus.String(modem_signal_iface)][
                           dbus.String('Lte')].keys())):
        
        cell_tech = 'Lte'

    else:

        cell_tech = 'Umts'

#Get RSSI data from the dictionary. If there is still no data, assume the modem
#ID has changed and needs to have the signal info update rate set.

    try:
        
        rssi = modem_data[dbus.ObjectPath(modem_path)][
                          dbus.String(modem_signal_iface)][
                          dbus.String(cell_tech)][dbus.String('rssi')]
        
    except(KeyError):
        
        set_update_rate(modem_path)

        return ''

    return [int(float(rssi)),cell_tech]

#Assign a signal quality retrieval refresh rate of 1 second using the 'Setup()'
#method of the 'Signal' object for the modem in modem_path.

def set_update_rate(modem_path):

    modem_object = bus.get_object('org.freedesktop.ModemManager1', modem_path)
    modem_iface = dbus.Interface(modem_object,
                                 'org.freedesktop.ModemManager1.Modem.Signal')
    modem_iface.Setup(dbus.UInt32(1))

def write_to_csv(timestamp, signal, cell_tech):


    with open('/data/log/cell.csv', mode = 'a') as log:

        log = csv.writer(log, delimiter = ',', quotechar = '"',
                         quoting = csv.QUOTE_MINIMAL)

        log.writerow([timestamp, signal, cell_tech])


def write_to_db(timestamp, signal, cell_tech):

    db.run("INSERT INTO cell (time, signal, cell_tech) VALUES (to_timestamp(%s), \
            %s, %s)", (timestamp, signal, cell_tech))

    print("Finished inserting cell signal power data for timestamp ", timestamp)

#Initialize postgres database

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
          signal int2 NOT NULL,
          cell_tech text NOT NULL);""")

print("Ensuring cell data table is a timescaledb hypertable")
db.run("""
        SELECT create_hypertable('cell', 'time', if_not_exists => TRUE,  
        migrate_data => TRUE);""")

print("Finished setting up tables")

#Initialize DBus system bus

bus = dbus.SystemBus()

while(True):

    timestamp = int(time.time()) 

    [signal, cell_tech] = get_modem_rssi()
    
    if (signal != ''):

        write_to_csv(timestamp, signal, cell_tech)
        write_to_db(timestamp, signal, cell_tech)

    time.sleep(1)
