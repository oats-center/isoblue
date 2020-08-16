#!/usr/bin/env python3

import requests   # Used to get docker-compose from server
import os         # Used to check for existence of docker-compose files, move, and delete them
import sys        # Used to exit the program
import subprocess # Used to interact with docker-compose
import socket     # Used to get hostname
import docker     # For interacting with the docker containers

# General program flow:
# 1. Get docker-compose.yml from server use `docker-compose config` to validate
#    a. If server docker-compose.yml file is not valid, exit
# 2. Use `docker-compose config` to generate 'validated' version of local config
# 3. Check if generated docker-compose.yml files differnt
# 4. Check if any docker containers can been update. Pull images if so. 
# 5. If docker-compose.yml files differ or if any docker containers were updated, shut down all containers and restart them

# Don't restart the containers unless there is an update to the containers or docker-compose
restartcontainers=False

# Get current docker-compose from the server
hostname = socket.gethostname()
url = 'http://172.16.0.1:8006/' + hostname + '/docker-compose.yml'
print('Querying server for docker-compose file')
response = requests.get(url)

# Ensure we got a valid response
print('Ensuring we got a valid response')
if response.status_code != 200:
    print('Got a HTTP response code ', response, '. Is there a docker-compose.yml file in the right location?')
    sys.exit()

# Extract the docker-compose
serverdc = response.content.decode('ascii')

# Validate docker-compose
open('./docker-compose.yml.new', 'w').write(serverdc)
print('Validating new docker-compose')
serverdc_config = subprocess.run(['docker-compose', '-f', './docker-compose.yml.new', 'config'], capture_output=True)
if serverdc_config.returncode != 0:
    print('Return code is not valid! Not using new docker-compose')
    os.remove('./docker-compose.yml.new')
    sys.exit()

if not os.path.isfile('./docker-compose.yml'):
    # If no current docker-compose, write it
    print('Writing initial docker-compose from server')
    os.rename('./docker-compose.yml.new', './docker-compose.yml')
    restartcontainers=True 
else:
    print('docker-compose file found, comparing to server version')

    # Get docker-compose config
    localdc_config = subprocess.run(['docker-compose', '-f', './docker-compose.yml', 'config'], capture_output=True)

    # If they are the same, exit
    if localdc_config.stdout.decode('ascii') == serverdc_config.stdout.decode('ascii'):
        print('Server and local docker-compose files are equivalent')
    else:
        # Write the new docker-compose
        print('Server and local docker-compose files are not the same. Replacing docker-compose and restarting all docker containers')
        os.rename('./docker-compose.yml.new', './docker-compose.yml')
        restartcontainers = True
        print('New docker-compose written')

# Check if any container needs updates


if restartcontainers:

    print('Connecting to docker daemon')
    # Connect to docker daemon
    client = docker.from_env()

    print('Stopping and removing currently running containers')
    for container in client.containers.list():
        container.stop()
        container.remove()
    
    # Use docker-compose to bring containers back up with new config
    print('Starting containers with docker-compose')
    subprocess.run(['docker-compose', '-f', 'docker-compose.yml', 'up', '-d'])

