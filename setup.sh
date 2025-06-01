#!/usr/bin/env bash
#
# SPDX-License-Identifier: CC-BY-4.0
# Copyright 2025, 2024, 2023 Bill Hass
#
# Setup script for setting up a vanilla Ubuntu 22.04 or 24.04 environment for class

set -euox pipefail

# Get latest apt package info
sudo apt update

# BitMagic Basic UI front-end
sudo apt install -y sigrok

# Serial terminal emulator
sudo apt install -y tio

# Make sure python is available and a virtual environment is configured
sudo apt install python3 python3-venv
python3 -m venv ./python
source ./python/bin/activate

# Tigard (ft2232h) python apps; see https://eblot.github.io/pyftdi/
python3 -m pip install pyftdi

# Setup for pyftdi; see https://eblot.github.io/pyftdi/installation.html#debian-ubuntu-linux 
sudo apt install -y libusb-1.0-0

tmpfile=$(mktemp)
if [ ! -f /etc/udev/rules.d/11-ftdi.rules ]; then
  cat << OUT > $tmpfile
# FT2232C/FT2232D/FT2232H
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", GROUP="plugdev", MODE="0664"
OUT
sudo mv $tmpfile /etc/udev/rules.d/11-ftdi.rules
fi

# Install OpenOCD
sudo apt install -y openocd

# Install UNIX binary RE tools
sudo apt install -y binutils

# Install an editor and hex editor
sudo apt install -y vim dhex

# Extract datasheets tar
if [ ! -d datasheets ]; then
  tar xzvf datasheets.tar.gz
fi
