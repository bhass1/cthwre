# SPDX-License-Identifier: CC-BY-4.0
# Copyright 2024 Bill Hass
#
# Test script for checking i2c comm is working with ST25DV64KC
#

from pyftdi.ftdi import Ftdi as ftdi
from st25dvxxkc import St25dv64kc
from os import environ

ftdi.show_devices()
ftdi_url = environ.get('FTDI_DEVICE', 'ftdi:///2')

i2c_ctrl = I2cController()
i2c_ctrl.configure(ftdi_url)
print(f'{i2c_ctrl.frequency=}')

st25dv = St25dv64kc(i2c_ctrl)

i2c_cfg_val = st25dv.get_i2c_ctrl()
print(f'{i2c_cfg_val=}')
uid_val = st25dv.get_device_UID()
print(f'{uid_val=}')

if st25dv.unlock_i2c():
    st25dv.lock_ccfile()
