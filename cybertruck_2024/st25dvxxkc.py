# SPDX-License-Identifier: CC-BY-4.0
# Copyright 2024 Bill Hass
#
# Basic class for interfacing with ST25DV64KC using pyftdi
#

from pyftdi.i2c import I2cController

# Taken from https://github.com/sparkfun/SparkFun_ST25DV64KC_Arduino_Library/blob/main/src/SparkFun_ST25DV64KC_Arduino_Library_Constants.h
enum ST25DV64KC_ADDR: 
    USER = 0x53
    SYS = 0x57
    RF_SWITCH_OFF = 0x51
    RF_SWITCH_ON = 0x55

UID_ADDR = 0x18
UID_LEN = 8 # bytes
I2C_CTRL_ADDR = 0x0E
I2C_CTRL_LEN = 1 # bytes
I2C_PWD_ADDR = 0x0900
I2C_PWD_LEN = 8 # bytes
I2C_SSO_DYN_ADDR = 0x2004
I2C_SSO_DYN_LEN = 1
LOCK_CCFILE_ADDR = 0x000C

class St25dv64kc:
    # pyftdi.ftdi.i2c docs https://eblot.github.io/pyftdi/api/i2c.html
    I2cController i2c_ctrl

    def __init__(self, i2c_ctrl: I2cController):
        self.i2c_ctrl = i2c_ctrl

    def get_device_UID(self) -> bytes:
    """ Read the device UID from system memory """
        return read_sys_mem(UID_ADDR, UID_LEN)

    def get_i2c_ctrl(self) -> bytes:
    """ Read the I2C_CTRL register from system memory """
        return read_sys_mem(I2C_CTRL_ADDR, I2C_CTRL_LEN)

    def get_i2c_security_status(self) -> bytes:
    """ Read the I2C_SSO_DYN register from user memory """
        return self.read_usr_mem(I2C_SSO_DYN_ADDR, I2C_SSO_DYN_LEN)

    def lock_ccfile(self) -> bytes:
    """ Write lock value to LOCK_CCFILE system register """
        return self.write_sys_mem(LOCK_CCFILE_ADDR, b'0x02')

    def read_sys_mem(self, addr: int, num_bytes: int) -> bytes:
    """ Read bytes with device select E2=1 & E1=1 (aka system memory) """
        i2c_port = self.i2c_ctrl.get_port(ST25DV64KC_ADDR.SYS)
        addr_bytes = (addr).to_bytes(2)
        return i2c_port.exchange(addr_bytes, num_bytes)

    def read_usr_mem(self, addr: int, num_bytes: int) -> bytes:
    """ Read bytes with device select E2=0 & E1=1 (aka user memory) """
        i2c_port = self.i2c_ctrl.get_port(ST25DV64KC_ADDR.USER)
        # User memory ends at 0x1fff on highest capacity variant "64" = 64 Kbit
        if addr > 0x1fff:
            raise IOError(f'Invalid user memory address {addr=}')
        addr_bytes = (addr).to_bytes(2)
        return i2c_port.exchange(addr_bytes, num_bytes)

    def write_sys_mem(self, addr: int, write_bytes: bytes) -> bytes:
    """ Write bytes with device select E2=0 & E1=1 (aka user memory) """
        i2c_port = self.i2c_ctrl.get_port(ST25DV64KC_ADDR.SYS)
        if addr == I2C_PWD_ADDR:
            raise IOError(f'Unable to write to this address {addr=}')
        addr_bytes = (addr).to_bytes(2)
        return i2c_port.exchange(addr_bytes + write_bytes, 0)
        
    def write_usr_mem(self, addr: int, write_bytes: bytes) -> bytes:
    """ Write bytes with device select E2=0 & E1=1 (aka user memory) """
        i2c_port = self.i2c_ctrl.get_port(ST25DV64KC_ADDR.USER)
        # User memory ends at 0x1fff on highest capacity variant "64" = 64 Kbit
        if addr > 0x1fff:
            raise IOError(f'Invalid user memory address {addr=}')
        addr_bytes = (addr).to_bytes(2)
        return i2c_port.exchange(addr_bytes + write_bytes, 0)


    def unlock_i2c(self) -> bool:
    """ Unlocks i2c for writing """
        security_status = self.get_i2c_security_status()
        if security_status == 1:
            print(f'Security Status already unlocked! Not attempting unlock')
            return True
        i2c_pwd = bytes(I2C_PWD_LEN)
        i2c_pwd_sequence = i2c_pwd + b'0x09' + i2c_pwd
        self.write_sys_mem(I2C_PWD_ADDR, I2C_PWD)
        security_status = self.get_i2c_security_status()
        if security_status == 1:
            print(f'Security unlocked Successfully!')
            return True
        else:
            print(f'Security unlocked Failed!')
            return False

