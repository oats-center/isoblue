#!/bin/bash

echo "$(ip route | awk '/default/ { print $3 }') host.docker.internal" >> /etc/hosts

./kafka-gps-log.py
