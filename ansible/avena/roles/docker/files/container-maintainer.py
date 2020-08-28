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
# 4. If docker-compose.yml files differ, shut down all containers and restart them

# Boolean to track if a container restart is needed
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
    print('docker-compose validation return code is not valid! Not using new docker-compose')
    os.remove('./docker-compose.yml.new')
    sys.exit()

# Write new docker-compose file if it differs
if not os.path.isfile('./docker-compose.yml'):
    # If no current docker-compose, write it
    print('Writing initial docker-compose from server')
    os.rename('./docker-compose.yml.new', './docker-compose.yml')
    restartcontainers=True

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
        print('Server and local docker-compose files are not the same. Replacing docker-compose and restarting all docker containers')
        os.rename('./docker-compose.yml.new', './docker-compose.yml')
        restartcontainers = True
        print('New docker-compose written')


print('Connecting to docker daemon')
# Connect to docker daemon
client = docker.from_env()

# Sanity check - the number of currently running containers should match the number of services 
# defined in the docker-compose file. There is probabally a more elegant way to do this, but the
# docker api does not appear to let you find the name of each service
running_services = subprocess.run(['docker-compose', '-f', './docker-compose.yml', 'config', '--services'], capture_output=True)
if len(client.containers.list()) != len(running_services.stdout.decode('ascii').strip().split('\n')):
    print('Restarting containers due to mismatch in number of running containers (running: ', len(client.containers.list()), ' config: ', len(running_services.stdout.decode('ascii').strip().split('\n')), ')' )
    restartcontainers = True
    

if restartcontainers:
    print('Stopping and removing currently running containers')
    for container in client.containers.list():
        container.stop()
        container.remove()
    
    # Use docker-compose to bring containers back up with new config
    print('Starting containers with docker-compose')
    dcup = subprocess.run(['docker-compose', '-f', 'docker-compose.yml', 'up', '-d'])
    
    # Check return code
    if dcup.returncode != 0:
        print("WARNING: docker-compose up command unsuccessful")
        sys.exit(-1)

