# Manual installing Debian on Toradex Apalis

_Note: This is our best effort guide. We only test with the automated
installation, but PRs with fixes/enhancements are always welcome._

1. Download the [`armhf` installer iso](https://cdimage.debian.org/debian-cd/current/armhf/iso-cd/debian-10.3.0-armhf-netinst.iso)
2. Download the [`installer-armhf` image](http://http.us.debian.org/debian/dists/buster/main/installer-armhf/current/images/hd-media/hd-media.tar.gz)
3. Format a USB stick to one FAT32 partition.
4. Un-gzip and un-tar `hd-media.tar.gz` to the USB stick root (`tar zxvf hd-media.tar.gz`)
5. Copy the `armhf` installer iso to USB stick root.
6. Connect to the serial interface of the Apalis board [as shown
   here](https://developer.toradex.com/getting-started/module-1-from-the-box-to-the-shell/unboxing-and-setup-cables-ixora-torizon?som=apalis-imx8&board=ixora-carrier-board&os=torizon&desktop=linux#step-2)
7. Immediately after pressing the power button, hit any key to stop the boot process and fall into the U-Boot
   shell.
8. With the installer USB stick inserted, run

   1. Type `setenv fdtfile imx6q-apalis-ixora-v1.1.dtb` (for Apalis V1.1) or
      `setenv fdtfile imx6q-apalis-ixora.dtb` (for Apalis V1.0)
   2. Type `setenv bootargs "url=... auto=true domain=local hostname=avena-pre-deploy`
   3. Type `run bootcmd_usb0` to boot the Debian installer.

9. Run through the Debian installer. Avena will put most of its data in the
   `/data` directory. A dedicated `/boot` directory is needed if `lvm` is in
   use. You may want to consult the standard partitioning scheme as Avena may
   occasionally assume it.
10. Execute a shell before quiting the Debian installer and copy either the
    `imx6q-apalis-ixora.dtb` or `imx6q-apalis-ixora-v1.1.dtb` file from the
    `/lib/linux-image-*/` directory to `/boot`
11. Reboot and drop into the U-Boot shell. Run

    - `env default -a`
    - `setenv devtype 'sata'`
    - `setenv devnum 0`
    - `setenv partition 1`
    - `setenv fdtfile <path-to-fdtfile>`
    - `setenv bootargs 'bootargs=vmalloc=400M user_debug=30 ip=off root=<root-dev-file> ro rootfstype=<root-fs-type> rootwait consoleblank=0 no_console_suspend=5 console=tty1 console=ttymxc0,115200n8 mxc_hdmfbmem=32M'`
    - `setenv bootcmd 'sata init; ext4load ${devtype} ${devnum}:${partition} ${kernel_addr_r} /vmlinuz; ext4load ${devtype} ${devnum}:${partition} ${fdt_addr_r} /${fdtfile}; ext4load ${devtype} ${devnum}:${partition} ${ramdisk_addr_r} /initrd.img; bootz ${kernel_addr_r} ${ramdisk_addr_r}:${filesize} ${fdt_addr_r}'`
    - `saveenv`

    Replacing all `<...>` with their correct values for your system. If you are
    using the eMMC and/or your boot partition is not the first one, then the
    other U-Boot env variables may need to be modified as well.

12. Reboot the board and Debian should boot.
