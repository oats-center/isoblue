#!/bin/bash

port=${port:-20001}
interface=${interface:-docker0}
uname -a
/usr/src/app/socketcand -v -p $port -l $interface
