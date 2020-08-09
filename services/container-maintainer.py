#!/usr/bin/env python3

import requests   # Used to get docker-compose from server
import os.path    # Used to determine if there is already a local docker-compose file
import sys        # Used to exit the program
import subprocess # Used to interact with docker-compose
import socket     # Used to get hostname

# Get current docker-compose from the server
hostname = socket.gethostname()
url = 'http://172.16.0.1:8006/' + hostname + '/docker-compose.yml'
serverdc = requests.get(url).content.decode('ascii')

#TODO Ensure we don't have a 404, verify valid docker-compose

if not os.path.isfile('./docker-compose.yml'):
    # If no current docker-compose, write it and exit
    print('Writing initial docker-compose from server')
    open('./docker-compose.yml', 'w').write(serverdc)
    print('Exiting')
    sys.exit()

print('docker-compose file found, comparing to server version')

# Get docker-compose config
localdc = ''
with open ("./docker-compose.yml", "r") as openfile:
    localdc = openfile.read()

# If they are the same, exit
if localdc == serverdc:
    print('Server and local docker-compose files are the same. Exiting')
    sys.exit()

# Write the new docker-compose
print('Server and local docker-compose files are not the same. Replacing docker-compose and restarting all docker containers')
open('./docker-compose.yml', 'w').write(serverdc)
print('New docker-compose written. Stopping and removing all docker containers')

# Get a list of the currently running docker containers
print('Getting current containers')
dockerps = subprocess.run(['docker', 'ps', '-a', '-q'], capture_output=True)

containers = dockerps.stdout.decode('ascii').split('\n')
if containers[-1] == '':
    del containers[-1]
print(containers)

if containers != []:
    # Stop all containers
    print('Stopping and removing current containers')
    subprocess.run(['docker', 'stop'] + containers ) 
    
    # Remove all containers
    print('Removing current containers')
    subprocess.run(['docker', 'rm'] + containers)

# Use docker-compose to bring containers back up with new config
print('Starting containers with docker-compose')
subprocess.run(['docker-compose', '-f', 'docker-compose.yml', 'up', '-d'])