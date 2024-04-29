# SPDX-License-Identifier: CC-BY-4.0
# Copyright 2024 Bill Hass
#
# Test script for checking basic i2c functionality with ST25DV64KC
#

from pyftdi.ftdi import Ftdi as ftdi
from pyftdi.i2c import I2cController
from st25dvxxkc import St25dv64kc, RFA1SS_ADDR
from os import environ

ftdi.show_devices()
ftdi_url = environ.get('FTDI_DEVICE', 'ftdi:///2')

i2c_ctrl = I2cController()
i2c_ctrl.configure(ftdi_url)
print(f'{i2c_ctrl.frequency=}')

st25dv = St25dv64kc(i2c_ctrl)

is_kc = st25dv.is_kc()
if is_kc:
    print(f'This is a "KC" series part')
    i2c_cfg_val = st25dv.get_i2c_ctrl()
    print(f'{i2c_cfg_val.hex()=}')
else:
    print(f'This is a "K" series part')

uid_val = st25dv.get_device_UID()
print(f'{uid_val.hex()=}')

if st25dv.unlock_i2c():
    print(f'{st25dv.read_sys_mem(RFA1SS_ADDR, 1).hex()=}')
