# Installing Debian on Toradex Apalis

Linux: Debian stable (at time of writing, Buster 10.3)

## Features

1. Automatic handling of differences between board v1.0 and v1.1
1. Consistent installs between all nodes
1. Automatic upgrades of device-tree files during future Linux kernel upgrades

## Assumptions

1. An external SSD is installed.
   - _Note: You can modify `preseed.cfg` to use the built in eMMC before
     building the installer disk, but at 4GB its not much use for most ISOBlue
     applications. Be sure to also update the U-Boot configuration._

## Installation steps

### Making installer disk (skip if you already have one)

_Note: If you need to change the default installation, modify the `preseed.cfg`
file suitably before continuing._

1. Ensure you have the necessary utilities on your computer (assuming Debian)

`$ sudo apt install util-linux u-boot-tools wget`

2. Insert a USB flash stick into your computer and determine its device file,
   e.g., `/dev/sda`. **Please be certain, the next step is destructive to any
   data on the device.**

3. Make installer disk:

   `$ ./installers/toradex-apalis/make-install-disk.sh DEVICE_FILE`

Where `DEVICE_FILE` is replaced by the file determined in step 2. Answer 'y' if
you are certain the `DEVICE_FILE` is correct.

### Installing Debian

4. Connect to the serial console of the Apalis as [described
   here](https://developer.toradex.com/getting-started/module-1-from-the-box-to-the-shell/unboxing-and-setup-cables-ixora-torizon?som=apalis-imx8&board=ixora-carrier-board&os=torizon&desktop=linux#step-2).

5. Connect the Apalis to the Internet via the Ethernet port.

6. Insert installer disk into the Apalis board, power cycle the unit, and
   quickly hit any key to stop U-Boot and fall into shell.

7. Boot the installer by entering the following into the U-Boot shell:

`usb start; load usb 0:1 ${scriptaddr} avena/install-avena.scr; source ${scriptaddr}`

8. The installation should begin and proceed to completion automatically, only
   stopping to ask for a password twice.

   Enter a password of your choice. You will need to remember what it is until
   Avena is fully deployed. It may also come in handy in future debugging.

9. After the installer reboots the board, Debian will start. Log in with the
   user name `avena` and password of your choice from step 8. Run `ip a`and note
   the boards IP address. Continue by installing Avena with Ansible.

_Note: The Debian installer does not always properly reboot the hardware. You
may have to manually power cycle the device._

## Known issues

- **Issue:** Wake-on-can does not work out of the box on Debian 10.4.

  **Solution:**: The current release of Avena upgrades to most recent
  [backports](https://backports.debian.org/) kernel, which contains the needed
  fix. You could also install a recent `linux-toradex` kernel. Either way, if
  Debian was installed manually, then it is also important to update the device
  tree file.

- **Issue:** Das U-Boot that comes by default with Toradex images does not know
  LVM.

  **Solution:** The automated installer for Apalis creates a dedicated `/boot`
  partition. U-Boot would need to be upgrade to support the Avena standard
  partitioning of `/boot` as a plain directory in logical `/` volume.
