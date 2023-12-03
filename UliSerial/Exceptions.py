#!/usr/bin/env python3

class UliSerialException(Exception):
    """
    Base class for all UliSerial exceptions.
    """
    pass

class NoSuchSerialPortException(UliSerialException):
    """
    Raised when a serial port cannot be found.
    """
    pass

class MultipleSerialPortsException(UliSerialException):
    """
    Raised when multiple serial ports match the given criteria.
    """
    pass