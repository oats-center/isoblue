#!/usr/bin/env bash
# RUN AS ROOT

count=0

# While true
while :
do 
	# Stuff
	echo -e "Test Cycle $count"
	export VAULT_ADDR="http://172.16.0.1:8200" && ./vault write -field=signed_key avena-client-signer/sign/admin public_key=@$HOME/.ssh/id_ed25519.pub > ~/.ssh/id_ed25519-cert.pub

	# With CAN on:
	#  Assert we can ping device
	#  ssh into device, turn on can watchdog
	#  await CAN to stop sending
        # With CAN off:
	#  sleep for 10s to let board sleep
	#  Assert we cannot ping device
	# With CAN on:
	#  sleep for 30s to let board boot
	#  ssh into device, turn off can watchdog
	#  await CAN to stop sending
	# With CAN off
	#  sleep for 10s to let board sleep
        #  Assert we can ping device	
	
	
	# Start a 120s CAN message salvo
	echo -e "Starting a 120s CAN message salvo"
	cangen can0 -g 1000 -I 42A -L 1 -D i -n 120 &
	echo -e "Sleeping for 60s to let board boot"
	sleep 60

	echo -e "Pinging board"
	ping -q -c 5 172.16.254.5 &>/dev/null
	ping5=$?
	
	if [[ "$ping5" != 0 ]]; then
		echo -e "The board did not respond to the ping with can messages on the bus"
		exit 0;
	fi

	echo -e "Turning on can-watchdog"
	cat dev-05.txt | ssh -tt avena@172.16.254.5 docker unpause container-maintainer_can-watchdog_1 #sudo systemctl start can-watchdog.service
	
	echo -e "Sleeping for 90s to let can messages stop"
	sleep 90

	echo -e "Sleeping for 30s to let the board sleep"
	sleep 30

     	echo -e "Pinging board"
	ping -q -c 1 172.16.254.5 &>/dev/null
	ping5=$?
	
	if [[ "$ping5" == 0 ]]; then
		echo -e "The board responded to the ping with can-watchdog on and no can messages on the bus"
		exit 0;
	fi

	echo -e "Starting a 120s CAN messsage salvo"
	cangen can0 -g 1000 -I 42A -L 1 -D i -n 120 &
	echo -e "Sleeping for 90s to let board boot"
	sleep 90

	echo -e "Pinging board"
	ping -q -c 5 172.16.254.5 &>/dev/null
	ping5=$?
	
	if [[ "$ping5" != 0 ]]; then
		echo -e "The board did not respond to the ping with can messages on the bus"
		exit 0;
	fi

	echo -e "Turning off can-watchdog"
	cat dev-05.txt | ssh -tt avena@172.16.254.5 docker pause container-maintainer_can-watchdog_1 #sudo systemctl stop can-watchdog.service
	echo -e "Sleeping for 90s to let can messages stop"
	sleep 90

	echo -e "Sleeping for 30s to let the board sleep"
	sleep 30
	
	echo -e "Pinging board"
	ping -q -c 5 172.16.254.5 &>/dev/null
	ping5=$?
	
	if [[ "$ping5" != 0 ]]; then
		echo -e "The board did not respond to the ping with can-watchdog disabled and no can messages on the bus"
		exit 0;
	fi
	echo -e "Ping successful\n"
	((count++))
done

