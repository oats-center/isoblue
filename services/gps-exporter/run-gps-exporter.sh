#!/bin/bash

echo "\$db_user = $db_user" > /proc/1/fd/1 2>&1
echo "\$db_host = $db_host" > /proc/1/fd/1 2>&1
echo "\$db_database = $db_database" > /proc/1/fd/1 2>&1
echo "\$from = $from" > /proc/1/fd/1 2>&1
echo "\$segment_length = $segment_length" > /proc/1/fd/1 2>&1

/app/gps-exporter postgress://$db_user:$db_password@$db_host:$db_port/$db_database /data -f "$from" -l $segment_length --append > /proc/1/fd/1 2>&1
