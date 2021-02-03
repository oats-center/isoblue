# Installing Debian on LattePanda Alpha/Delta

Linux: Debian stable (at time of writing, Buster 10.7)

## Features

1. Use of a preseed file for automated and identical installs across multiple installs.

## Assumptions

1. You have access to a Linux desktop to flash the installer image to a USB
  drive. If you are using Windows, you can use tools such as
  [rufus](https://github.com/pbatard/rufus), but that will not be covered in
  this guide.

1. An external SSD is installed.
   - _Note: If your LattePanda board has an internal MMC, you can modify
      `preseed.cfg` to use the built in eMMC but at 32 - 64GB will be difficult 
      to use for an extended time without frequent log retrieval and removal._
   - We are assuming that if you are using a LattePanda Alpha, you are using a
      SATA SSD and if you are using a LattePanda Delta you are using a NVMe SSD.
      If this is not the case, you should modify your preseed file accordingly.
      You should expect to change the `/dev/sda` or `/dev/nvme0n1` entries in the
      partman section to the appropriate device path of the SSD installed in your
      system.

## Installation steps

### Making installer disk

1. Download the appropriate Debian image. We recommend the unofficial 'firmware'
   build to ensure that devices such as the NVMe drives and wifi cards work out
   of the box. In our experience, the Delta requires with build to properly detect
   the NVMe SSD and install successfully. The guide was made using the
   `firmware-10.7.0-amd64-DVD1.iso` build found [here](https://ftp.acc.umu.se/debian-cd/10.7.0/amd64/iso-dvd/).

1. Insert a USB flash stick into your computer and determine its device file,
   e.g., `/dev/sda`. This can be done with the `lsblk` command or similar.
   **Please be certain, the next step is destructive to any
   data on the device.**

1. Make installer disk:

   `$ sudo dd bs=4M if=/path/to/iso/firmware-10.7.0-amd64-DVD-1.iso \`
   `of=DEVICE_FILE conv=fdatasync status=progress`

Where `DEVICE_FILE` is replaced by the file determined in step 2

### Installing Debian

_Note: If you need to change the default installation, modify the `preseed.cfg`
file suitably before continuing._

1. Connect the LattePanda to a monitor with an HDMI cord, connect the LattePanda
   to the Internet via the Ethernet port, plug in a keyboard to one of the usb
   plugs, and connect the USB C power plug.

1. Insert installer disk into the LattePanda board, power cycle the unit,
   repeatedly and hit F7 until the boot selection screen pops up, and then select
   the USB drive.

1. Navigate to "Advanced Install", and then select "Automated Install".

1. The installer will ask you for an address of the `preseed.cfg` file. If you
   have the repository cloned on your development machine and it is on the same
   LAN, you can use `python3 -m http.server 8080` within the appropriate
   `installers/lattepanda-*` directory and enter `dev-machine-ip/preseed.cfg`.
   The guide was written using this method. Otherwise, you can use the
   following link to the most recent stable version:
     - Alpha: `https://github.com/oats-center/isoblue-avena/blob/master/installers/lattepanda-alpha/preseed.cfg`
     - Delta: `https://github.com/oats-center/isoblue-avena/blob/master/installers/lattepanda-delta/preseed.cfg`

1. The installation should begin and proceed to completion automatically, only
   stopping to ask for a password twice.

   Enter a password of your choice. You will need to remember what it is until
   Avena is fully deployed. It may also come in handy in future debugging.

1. After the installer reboots the board, Debian will start. Log in with the
   user name `avena` and password of your choice from step 8. Run `ip a`and note
   the boards IP address. Continue by installing Avena with Ansible.

_Note: The Debian installer does not always properly reboot the hardware. You
may have to manually power cycle the device._

## Known issues

- **Issue:** Wake-on-can does not work out of the box on Debian 10.4.

  **Solution:**: The current release of Avena upgrades to most recent
  [backports](https://backports.debian.org/) kernel, which contains the needed
  fix.
