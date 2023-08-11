#!/usr/bin/env bash
# RUN AS ROOT?

# Setup GPIO Pins
echo -e "Setting up GPIO Pins"
#echo 37 > /sys/class/gpio/export
#echo "out" > /sys/class/gpio/gpio37/direction

echo '#####################'
echo '## Hard Reset Test ##'
echo '#####################'

# While true
for i in {0..5} 
do 
	# Stuff
	echo -e "Hard reset $i"
	# Turn off outlet
	#echo -e "Removing power from boards under test"
	echo 1 > /sys/class/gpio/gpio37/value

	# Sleep 5s to allow everything to drain
	#echo -e "Sleeping 5s"
	sleep 5

	# Turn on outlet
	#echo -e "Restoring power to boards under test"
        echo 0 	> /sys/class/gpio/gpio37/value

	currtime=$(date +%s)
	ping5=999
	ping6=999

	# While ping unsuccessful
	while [[ "$ping5" != 0 ]] || [[ "$ping6" != 0 ]]; do

		# Sleep for 1 second
		#echo -e "\tSleeping for 1s"
		sleep 1
		
		# If we exceed 10 mins (600s) and both are not up
		#echo -e "\tChecking if we have been waiting for more than 10mins"
		timediff=$(($(date +%s)-$currtime))
		if [ $timediff -gt 600 ]; then
			echo -e "One of the boards did not come back online:\n5: $ping5\t6: $ping6\n"
			exit 0;
		fi

		# Ping boards
		#echo -e "\tPinging 5"
		ping -q -c 1 172.16.254.5 &>/dev/null
		ping5=$?
		#echo -e "\tPinging 6"
		ping -q -c 1 172.16.254.6 &>/dev/null
		ping6=$?
		#echo -e "\t5: $ping5\t6: $ping6"
	done
	timediff=$(($(date +%s)-$currtime))
	echo -e "\t5: $ping5\t6: $ping6\t$timediff s\n"
	((count++))
done


echo '#####################'
echo '## CAN Reset Test ##'
echo '#####################'
for i in {0..5} 
do 
	echo -e "Hard reset $i"
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


echo '######################'
echo 'Test Finished: Success
