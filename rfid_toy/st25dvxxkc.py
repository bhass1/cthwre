# SPDX-License-Identifier: CC-BY-4.0
# Copyright 2024 Bill Hass
#
# Basic class for interfacing with ST25DV64KC using pyftdi
# pyftdi.ftdi.i2c docs: <https://eblot.github.io/pyftdi/api/i2c.html>
#

from enum import IntEnum, Enum
from pyftdi.i2c import I2cController

# Taken from https://github.com/sparkfun/SparkFun_ST25DV64KC_Arduino_Library/blob/main/src/SparkFun_ST25DV64KC_Arduino_Library_Constants.h
class St25dvxxkxAddr(IntEnum):
    USER = 0x53
    SYS = 0x57
    RF_SWITCH_OFF = 0x51
    RF_SWITCH_ON = 0x55

class St25dvxxkxIcRef(Enum):
    ST25DV04K = 0x24
    ST25DV16K = 0x26
    ST25DV64K = 0x26
    ST25DV04KC = 0x50
    ST25DV16KC = 0x51
    ST25DV64KC = 0x51

IC_REF_ADDR = 0x0017
IC_REF_LEN = 1 # bytes
UID_ADDR = 0x18
UID_LEN = 8 # bytes
I2C_CTRL_ADDR = 0x0E
I2C_CTRL_LEN = 1 # bytes
I2C_PWD_ADDR = 0x0900
I2C_PWD_LEN = 8 # bytes
I2C_SSO_DYN_ADDR = 0x2004
I2C_SSO_DYN_LEN = 1 # bytes
RFA1SS_ADDR = 0x0004
RFA2SS_ADDR = 0x0006
RFA3SS_ADDR = 0x0008
RFA4SS_ADDR = 0x000A
LOCK_CCFILE_ADDR = 0x000C
LOCK_CFG_ADDR = 0x000F

class St25dv64kc:
    _i2c_ctrlr: I2cController

    def __init__(self, i2c_ctrlr: I2cController):
        self._i2c_ctrlr = i2c_ctrlr

    def is_kc(self) -> bool:
        """ Return True if device is a 'KC' series part, False if 'K' series part 

            Note that 'KC' series is newer and has programmable I2C addresses among other 
            mostly minor differences.
        """
        ic_ref = int.from_bytes(self.read_sys_mem(IC_REF_ADDR, IC_REF_LEN), "big")
        if ic_ref in [St25dvxxkxIcRef.ST25DV04KC.value, St25dvxxkxIcRef.ST25DV16KC.value, 
            St25dvxxkxIcRef.ST25DV64KC.value]:
            return True
        elif ic_ref in [St25dvxxkxIcRef.ST25DV04K.value, St25dvxxkxIcRef.ST25DV16K.value, 
            St25dvxxkxIcRef.ST25DV64K.value]:
            return False
        else:
            raise RuntimeError(f'IC_REF value ({hex(ic_ref)}) does not match any expected value')

    def get_device_UID(self) -> bytes:
        """ Read the device UID from system memory """
        return self.read_sys_mem(UID_ADDR, UID_LEN)

    def get_i2c_ctrl(self) -> bytes:
        """ Read the I2C_CTRL register from system memory

            Note that the I2C_CTRL register does not exist for 'K' series parts.
            It's better to check with `is_kc` before making this function call.
        """
        return self.read_sys_mem(I2C_CTRL_ADDR, I2C_CTRL_LEN)

    def get_i2c_security_status(self) -> bytes:
        """ Read the I2C_SSO_DYN register from user memory """
        return self.read_usr_mem(I2C_SSO_DYN_ADDR, I2C_SSO_DYN_LEN)

    def lock_ccfile(self) -> bytes:
        """ Write lock value to LOCK_CCFILE system register """
        return self.write_sys_mem(LOCK_CCFILE_ADDR, b'\x03')

    def lock_cfg(self) -> bytes:
        """ Write lock value to LOCK_CFG system register """
        return self.write_sys_mem(LOCK_CFG_ADDR, b'\x01')

    def lock_rfa1ss(self) -> bytes:
        """ Write lock value to LOCK_CFG system register """
        return self.write_sys_mem(RFA1SS_ADDR, b'\x0c')

    def read_sys_mem(self, addr: int, num_bytes: int) -> bytes:
        """ Read bytes with device select E2=1 & E1=1 (aka system memory) """
        i2c_port = self._i2c_ctrlr.get_port(St25dvxxkxAddr.SYS)
        addr_bytes = (addr).to_bytes(2, byteorder='big')
        return i2c_port.exchange(addr_bytes, num_bytes)

    def read_usr_mem(self, addr: int, num_bytes: int) -> bytes:
        """ Read bytes with device select E2=0 & E1=1 (aka user memory) """
        i2c_port = self._i2c_ctrlr.get_port(St25dvxxkxAddr.USER)
        addr_bytes = (addr).to_bytes(2, byteorder='big')
        return i2c_port.exchange(addr_bytes, num_bytes)

    def write_sys_mem(self, addr: int, write_bytes: bytes, poll: int = 0) -> bytes:
        """ Write bytes with device select E2=0 & E1=1 (aka user memory) """
        i2c_port = self._i2c_ctrlr.get_port(St25dvxxkxAddr.SYS)
        if addr == I2C_PWD_ADDR:
            if write_bytes[8] == 0x07:
                raise IOError(f'Unable to write to this address {addr=}')
        addr_bytes = (addr).to_bytes(2, byteorder='big')
        read_bytes = i2c_port.exchange(addr_bytes + write_bytes, 0)
        if poll:
            count = poll
            print(f'Waiting for write', end='')
            for i in range(0, count):
                if i2c_port.poll(write=True, relax=False):
                    print(f'\nWriting finished!')
                    break
                else:
                    print('.', end='')
                if i == (count - 1):
                    print(f'\nWriting failed!')
        return read_bytes
        
    def write_usr_mem(self, addr: int, write_bytes: bytes, poll: int = 0) -> bytes:
        """ Write bytes with device select E2=0 & E1=1 (aka user memory) """
        i2c_port = self._i2c_ctrlr.get_port(St25dvxxkxAddr.USER)
        addr_bytes = (addr).to_bytes(2, byteorder='big')
        read_bytes = i2c_port.exchange(addr_bytes + write_bytes, 0)
        if poll:
            count = poll
            print(f'Waiting for write', end='')
            for i in range(0, count):
                if i2c_port.poll(write=True, relax=False):
                    print(f'\nWriting finished!')
                    break
                else:
                    print('.', end='')
                if i == (count - 1):
                    print(f'\nWriting failed!')
        return read_bytes

    def unlock_i2c(self) -> bool:
        """ Unlocks i2c for writing by opening i2c security session """
        security_status = self.get_i2c_security_status()
        if security_status == b'\x01':
            print(f'I2C already unlocked! Not attempting unlock')
            return True
        i2c_pwd = bytes(I2C_PWD_LEN)
        i2c_pwd_sequence = i2c_pwd + b'\x09' + i2c_pwd
        self.write_sys_mem(I2C_PWD_ADDR, i2c_pwd_sequence)
        security_status = self.get_i2c_security_status()
        if security_status == b'\x01':
            print(f'I2C unlocked successfully!')
            return True
        else:
            print(f'I2C unlock failed!')
            return False

