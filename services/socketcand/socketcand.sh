#!/bin/bash

port=${port:-20001}
interface=${interface:-docker0}
can_interfaces=${can_interfaces:can0,can1}

/usr/src/app/socketcand -v -p $port -l $interface -i $can_interfaces
