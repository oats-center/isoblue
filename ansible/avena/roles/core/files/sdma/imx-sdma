#!/bin/sh

PREREQ="udev"
prereqs()
{
	echo "$PREREQ"
}

if [ "$1" = "prereqs" ]; then
	prereqs
	exit 0
fi

# source functions
. /usr/share/initramfs-tools/hook-functions

# copy firmware
# first, the common ones, if any
if [ -d "/lib/firmware/imx/sdma" ]; then
	mkdir -p $DESTDIR/lib/firmware/imx/sdma
	cp /lib/firmware/imx/sdma/*.bin $DESTDIR/lib/firmware/imx/sdma/
fi

# now copy version-specific ones if any
if [ -d "/lib/firmware/${version}/imx/sdma" ]; then
	mkdir -p  $DESTDIR/lib/firmware/${version}/imx/sdma
	cp /lib/firmware/${version}/imx/sdma/*.bin $DESTDIR/lib/firmware/${version}/imx/sdma/
fi

# finally install kernel module (if it is a module)
manual_add_modules imx-sdma
