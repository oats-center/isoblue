#!/usr/bin/env bash

set +e

if [[ -z "$1" ]]; then
  echo >&2 "Usage: $0 BLOCK_DEVICE"
  exit 1
fi

if ! [ $(id -u) = 0 ]; then
   echo >&2 "This script requires root. Please run as root."
   exit 2
fi

dev=$1

if [[ ! -b "$dev" ]]; then
  echo >&2 "You must provide a block device to build installer on"
  exit 2
fi

read -p "All paritions will be deleted. Do you wish to continue? [y/N]" yn
case $yn in
  [Yy]* ) ;;
  * ) exit ;;
esac

# Make sure device is unmounted
for n in "${dev}*"; do
  umount $n || /bin/true
done

# Delete all partitions
sfdisk --delete "$dev"

# Make entire disk one partition
echo ';' | sfdisk "$dev"

fsdev="${dev}1"

# Format partition fat32
mkfs.vfat "$fsdev"

# Make a mount point and mount
d=$(mktemp -d)
mount "$fsdev" "$d"

# Build installer
wget -P "$d/" https://cdimage.debian.org/debian-cd/current/armhf/iso-cd/debian-10.4.0-armhf-netinst.iso
wget -O- http://http.us.debian.org/debian/dists/buster/main/installer-armhf/current/images/hd-media/hd-media.tar.gz | tar -zxf - -C "$d/"

mkdir -p "${d}/avena"

echo "Making Avena install u-boot script"
mkimage -T script -C none -n 'Install Avena on Apalis' -d install-avena "${d}/avena/install-avena.scr"

echo "Copying Debian preseed file"
cp preseed.cfg "${d}/avena"

echo "Copying device tree update script"
cp update-device-tree "${d}/avena"

echo "Unmounting installer"
umount "$d"
