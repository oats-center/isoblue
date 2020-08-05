#!/usr/bin/env python3

import requests
import os.path
import sys 

# Get current docker-compose from the server
url = 'http://172.16.0.1:8006/avena-apalis-dev06/docker-compose.yml'
dc = requests.get(url)

if not os.path.isfile('./docker-compose.yml'):
    # If no current docker-compose, write it and exit
    print('Writing itital docker-compose from server')
    open('./docker-compose.yml', 'wb').write(dc.content)
    print('Exiting')
    sys.exit()

print('docker-compose file found, comparing to server version')
# Get docker-compose config
