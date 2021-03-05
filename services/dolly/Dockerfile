FROM rclone/rclone:latest
# Add file containing new crontab entries
ADD crontab /crontab
# Append these entries to the root crontab
RUN cat /crontab >> /etc/crontabs/root && rm /crontab
# Make the folder for periodic rclone scripts
RUN mkdir /etc/periodic/rclone
# Add rclone sync script
# Name CANNOT have any special chars (No extension!)
ADD go-dolly /etc/periodic/rclone/go-dolly
# Make script executable
RUN chmod +x /etc/periodic/rclone/go-dolly

# Print out crontab and the time for debugging, start crond
# -l controls level out debugging output, 0 being the most
# Printing/rediring output to /proc/1/fd/1 prints it out in
# Docker's logs. It's a hack, deal with it or open a PR.
ENTRYPOINT crontab -l && echo "The time is $(date +%Y/%m/%d-%H:%M:%S)" && crond -f -l 8 -L /proc/1/fd/1
