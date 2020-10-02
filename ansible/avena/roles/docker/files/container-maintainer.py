#!/usr/bin/env python3

import requests         # Used to get docker-compose from server
import os               # Used to check for existence of docker-compose files, move, and delete them
import sys              # Used to exit the program
import subprocess       # Used to interact with docker-compose
import socket           # Used to get hostname
from time import sleep # For sleeping between pings to the docker-compose server

# General program flow:
# 1. Get docker-compose.yml from server use `docker-compose config` to validate
#    a. If server docker-compose.yml file is not valid, exit
# 2. Use `docker-compose config` to generate 'validated' version of local config
# 3. Check if generated docker-compose.yml files differnt. Replace docker-compose file if it differs
# 4. Run docker-compose pull && docker-compose up -d --remove orphans to update contianers

def update_compose_file():
    # Get current docker-compose from the server
    hostname = socket.gethostname()
    url = 'http://172.16.0.1:8006/' + hostname + '/docker-compose.yml'
    print('Querying server for docker-compose file')
    response = requests.get(url)
    
    # Ensure we got a valid response
    print('Ensuring we got a valid response')
    if response.status_code != 200:
        print('Got a HTTP response code ', response, '. Is there a docker-compose.yml file in the right location?')
        return

    # Extract the docker-compose
    serverdc = response.content.decode('ascii')
    
    # Validate docker-compose
    open('./docker-compose.yml.new', 'w').write(serverdc)
    print('Validating new docker-compose')
    serverdc_config = subprocess.run(['docker-compose', '-f', './docker-compose.yml.new', 'config'], capture_output=True)
    
    if serverdc_config.returncode != 0:
        print('docker-compose validation return code is not valid! Not using new docker-compose')
        os.remove('./docker-compose.yml.new')
        return
    
    # Write new docker-compose file if it differs
    if not os.path.isfile('./docker-compose.yml'):
        # If no current docker-compose, write it
        print('Writing initial docker-compose from server')
        os.rename('./docker-compose.yml.new', './docker-compose.yml')
    
    else:
        print('local docker-compose file found, comparing to server version')
    
        # Get docker-compose config
        localdc_config = subprocess.run(['docker-compose', '-f', './docker-compose.yml', 'config'], capture_output=True)
    
        # Check if docker-compose files are the same
        if localdc_config.stdout.decode('ascii') == serverdc_config.stdout.decode('ascii'):
            print('Server and local docker-compose files are equivalent')
            os.remove('./docker-compose.yml.new')
    
        else:
            # Write the new docker-compose
            print('Server and local docker-compose files are not the same. Replacing docker-compose and running docker-compose up')
            os.rename('./docker-compose.yml.new', './docker-compose.yml')
            print('New docker-compose written')


def update_containers():
    # Ensure that all current containers are the newest version
    print('Executing docker-compose pull to get new versions of current containers');
    
    dcpull = subprocess.run(['docker-compose', '-f', 'docker-compose.yml', 'pull'])
    
    # Check return code
    if dcpull.returncode != 0:
        print('WARNING: docker-compose pull command unsuccessful. Attempting to continue');
    
    print('Updating containers with docker-compose up -d --remove-orphans')
    dcup = subprocess.run(['docker-compose', '-f', 'docker-compose.yml', 'up', '-d', '--remove-orphans'])
    
    # Check return code
    if dcup.returncode != 0:
        print("FATAL: docker-compose up command unsuccessful")
        sys.exit(-1)


# Ensure we can reach the server (sometimes wireguard takes some time to boot up)
print('Ensuring we can reach the server')
failcnt = 0
pingretcode = os.system("ping -c 1 172.16.0.1 2>&1 >/dev/null")
while pingretcode != 0 and failcnt < 60:
    print('Server unreachable, retry num', failcnt, 'in 10 seconds')
    sleep(10)
    failcnt = failcnt + 1
    print('Retrying...')
    pingretcode = os.system("ping -c 1 172.16.0.1")

if pingretcode:
    print("Docker compose server is unreachable but we might still be able to pull new images. Doing so now")
else:
    print('Server reachable, continuing')
    update_compose_file()


if os.path.isfile('./docker-compose.yml'):
    update_containers()   
else:
    print('FATAL: No docker-compose file available')
    sys.exit(-1)
