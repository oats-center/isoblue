#!/usr/bin/env bash

# Arrays for keeping track of when each ISOBlue was last seen if it is currently online
last_seen=(0 0 0 0 0 0 0 0 0 0 0 0 0) # Timestamp of last time the isoblue was online
curr_online=(0 0 0 0 0 0 0 0 0 0 0 0 0) # Boolean if the isoblue last ping was successful

function=(	"Placeholder"\
		"[Ault] Hagie-Sts10-Sprayer"\
		"[Ault] 160-puma-tractor"\
		"[Ault] STX450-quadtrac"\
		"[Ault] 165-feeder"\
		"[Ault] 245-magnum-tractor"\
		"[Ault] Steiger450-quadtrac"\
		"[Balmos] reboot test/ACRE"\
		"[JVK] Unit #1"\
		"[JVK] Unit #2"\
		"[JVK] Unit #3"\
		"[JVK] Unit #4"\
		)

# Time to sleep between checks
sleeptime=$((60*1))

# Prefix of IP subnet to check
# TODO: This way really limits what IPs we can check
#       Make an iterable list of IPs to check in the future
prefix=172.16.1.


# If our state files do not exists, create them and populate them
# If not, read these files
scriptdir=~/.find-online
if [ ! -d $scriptdir ]; then
	mkdir $scriptdir
fi
last_seen_filepath=$scriptdir'/last_seen'
curr_online_filepath=$scriptdir'/curr_online'

# Last_seen array ffile
if [ ! -f $last_seen_filepath ]; then
	echo "Creating last_seen state file"
	touch $last_seen_filepath
	echo "${last_seen[*]}" > $last_seen_filepath
else
	echo "Reading last_seen state file"
	read -a last_seen < $last_seen_filepath
fi

# Currently online array file
if [ ! -f $curr_online_filepath ]; then
	echo "Creating online state file"
	touch $curr_online_filepath
	echo "${curr_online[*]}" > $curr_online_filepath
else
	echo "Reading online state file"
	read -a curr_online < $curr_online_filepath
fi

# Main ping loop
while :
do
	echo -e "Starting ping scan at $(date)"
	# Iterate through 172.16.0.1 ... 172.16.0.6
	for suffix in {1..11} 
	do
		if [ "$suffix" -eq "7" ]; then
			continue
		fi
		# If the ping is successful and the previous one was not
		if ping -q -c 1 $prefix$suffix &>/dev/null; then
			if [ ${curr_online[$suffix]} -eq 0 ]; then
				# Calculate last seen, update arrays
				echo -e "Ping $prefix$suffix successful\n\tLast online: $(date --date @${last_seen[$suffix]})"
				prev=${last_seen[$suffix]}
				gap=$(($(date +%s)-$prev))
				last_seen[$suffix]=$(date +%s)	
				curr_online[$suffix]=1

				# Notify user
				echo -e "\tNotifying user that $prefix$suffix just came online"
				gapstr=$(eval "echo $(date -ud "@$gap" +'$((%s/3600/24)) days %H hours %M minutes %S seconds')")
				if [ ${last_seen[$suffix]} -eq 0 ]; then
					message="{\"text\":\"${function[$suffix]} ($prefix$suffix) came online after $gapstr. Last seen partying with Jimmy Hendrix at Woodstock in '69\"}"
				else
					message="{\"text\":\"${function[$suffix]} ($prefix$suffix) came online after $gapstr. Last seen: $(date --date @$prev)\"}" 
				fi
				curl -X POST -H 'Content-type: application/json' --data "$message" <webhook URL>				echo -e '\n'
			else
				echo "Ping $prefix$suffix successful, not notifying user"
				last_seen[$suffix]=$(date +%s)
			fi
		else
			# Ping was not successful. If it was previously online, also send a message
			echo "Ping $prefix$suffix unsuccessful"
			if [ ${curr_online[$suffix]} -eq 1 ]; then
				echo -e "\tNotifying user that $prefix$suffix just went offline"
				message="{\"text\":\"${function[$suffix]} ($prefix$suffix) just went offline\"}" 
				curl -X POST -H 'Content-type: application/json' --data "$message" <webhook URL> 
				echo -e '\n'
			fi
			curr_online[$suffix]=0
		fi
	done
	# Write current state to file incase script is cancelled
	echo -e "Scan finished, writing to state file"
	echo "${last_seen[*]}" > $last_seen_filepath
	echo "${curr_online[*]}" > $curr_online_filepath
	echo -e "Checking again in $sleeptime seconds\n"
	sleep $sleeptime
done
