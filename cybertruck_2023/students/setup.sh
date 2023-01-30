#!/usr/bin/env bash

set -euox pipefail

# BitMagic Basic UI front-end
sudo apt install sigrok

# Snap "classic" confinement only supported now; see https://github.com/tio/tio/issues/188
snap install tio --classic


# Tigard (ft2232h) python apps; see https://eblot.github.io/pyftdi/
pip3 install pyftdi

# Setup for pyftdi; see https://eblot.github.io/pyftdi/installation.html#debian-ubuntu-linux 
sudo apt install libusb-1.0-0

tmpfile=$(mktemp)
if [ ! -f /etc/udev/rules.d/11-ftdi.rules ]; then
  cat << OUT > $tmpfile
# FT2232C/FT2232D/FT2232H
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", GROUP="plugdev", MODE="0664"
OUT
sudo mv $tmpfile /etc/udev/rules.d/11-ftdi.rules
fi


