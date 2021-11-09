#!/usr/bin/env python3

import dbus
import datetime
import time
from pynats2 import NATSClient

def get_signal_stats():

    modem_signal_iface = 'org.freedesktop.ModemManager1.Modem.Signal'

    modem_manager_object = bus.get_object('org.freedesktop.ModemManager1', 
                                          '/org/freedesktop/ModemManager1')
    modem_manager_iface = dbus.Interface(modem_manager_object, 
                                         'org.freedesktop.DBus.ObjectManager')

    modem_data = modem_manager_iface.GetManagedObjects()

#Extract modem path from the DBus data dictionary

    modem_path = list(modem_data.keys())[0]    

#Check if the 'Lte' dictionary has signal values assigned. If no values are
#found, assume the modem is connected to a 'Umts' network.

    if(list(modem_data[modem_path][modem_signal_iface]['Lte'].keys())):
        
        cell_tech = 'Lte'

    else:

        cell_tech = 'Umts'

#Get signal info from the dictionary. If there is no data, assume the modem
#ID has changed and needs to have the signal info update rate reset.

    try:

        signal_dict = dict(modem_data[modem_path][modem_signal_iface][cell_tech])
        
        signal = {}

        for item in signal_dict:
            # Truncate all floats to 1 decimal point
            signal[str(item)] = float(f'{signal_dict[item]:.1f}')

        signal["tech"] = cell_tech.lower()

    except(KeyError):
        
        set_update_rate(modem_path)
        
        return ''
    
    return signal

bus = dbus.SystemBus()


def set_update_rate(modem_path):

    modem_object = bus.get_object('org.freedesktop.ModemManager1', modem_path)
    modem_iface = dbus.Interface(modem_object,
                                 'org.freedesktop.ModemManager1.Modem.Signal')
    modem_iface.Setup(dbus.UInt32(1))

print("Starting cell_nats")


if __name__ == '__main__':

    while(True): 
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = get_signal_stats()
        with NATSClient() as client:
            for item in data:
                client.publish(f'cell.{item}', 
                               payload=bytes(str({'value' : data[item],
                                                  'time' : timestamp}), 
                                                  'utf-8'))
        
        time.sleep(1) 
