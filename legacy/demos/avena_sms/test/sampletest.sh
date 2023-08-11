#!/usr/bin/env bash
# RUN AS ROOT

# Setup GPIO Pins
echo -e "Setting up GPIO Pins"
#echo 37 > /sys/class/gpio/export
#echo "out" > /sys/class/gpio/gpio37/direction

count=0

# While true
while :
do 
	# Stuff
	echo -e "Test Cycle $count"
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

