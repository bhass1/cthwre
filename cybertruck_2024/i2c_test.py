# SPDX-License-Identifier: CC-BY-4.0
# Copyright 2024 Bill Hass
#
# Test script for checking i2c comm is working with ST25DV64KC
#

from pyftdi.ftdi import Ftdi as ftdi
from pyftdi.i2c import I2cController
ftdi.show_devices()
from os import environ
ftdi_url = environ.get('FTDI_DEVICE', 'ftdi:///2')

# pyftdi.ftdi.i2c docs https://eblot.github.io/pyftdi/api/i2c.html
i2c_ctrl = I2cController()
i2c_ctrl.configure(ftdi_url)
print(f'{i2c_ctrl.frequency=}')

# Taken from https://github.com/sparkfun/SparkFun_ST25DV64KC_Arduino_Library/blob/main/src/SparkFun_ST25DV64KC_Arduino_Library_Constants.h
ST25DV64KC_ADDR_DATA = 0x53
ST25DV64KC_ADDR_SYS = 0x57
ST25DV64KC_RF_SWITCH_OFF = 0x51
ST25DV64KC_RF_SWITCH_ON = 0x55

print(f'Opening port on 0x{ST25DV64KC_ADDR_SYS:02x}')
i2c = i2c_ctrl.get_port(ST25DV64KC_ADDR_SYS)
i2c_cfg_val = i2c.exchange([0x00, 0x0E], 1)
print(f'{i2c_cfg_val=}')

UID_LEN = 8 # bytes
uid_val = i2c.exchange([0x00, 0x18], UID_LEN)
print(f'{uid_val=}')
