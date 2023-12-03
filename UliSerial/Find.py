#!/usr/bin/env python3
import serial.tools.list_ports

__all__ = ['find_serial_ports', 'find_serial_port', 'serial_port_info']

def find_serial_ports(**kwargs):
    """
    Find serial ports that match given criteria.

    This function searches through all available serial ports and returns a list of ports
    that match all provided keyword arguments. The keyword arguments can correspond to any
    attribute of the serial.tools.list_ports.ListPortInfo object, such as 'serial_number',
    'vid', 'pid', or 'description'.

    Parameters:
    **kwargs: Arbitrary keyword arguments. Each argument should correspond to an attribute
              of ListPortInfo objects. Ports will be filtered based on these arguments.

    Returns:
    list: A list of port names (strings) that match all provided criteria. If no ports match,
          an empty list is returned.

    Example:
    >>> find_ports(manufacturer='Arduino LLC')
    ['/dev/ttyACM0']
    """
    ports = serial.tools.list_ports.comports()
    matching_ports = []

    for port in ports:
        match = True
        for key, value in kwargs.items():
            if not hasattr(port, key) or getattr(port, key) != value:
                match = False
                break
        if match:
            matching_ports.append(port.device)

    return matching_ports

def find_serial_port(**kwargs):
    """
    Find a single serial port that matches given criteria.

    This function is similar to find_ports, but it is designed to return exactly one port
    that matches the provided criteria. If no ports or more than one port match the criteria,
    it raises an exception.

    Parameters:
    **kwargs: Arbitrary keyword arguments. Each argument should correspond to an attribute
              of ListPortInfo objects. The port will be filtered based on these arguments.

    Returns:
    str: The name of the single port that matches the criteria.

    Raises:
    ValueError: If no ports or more than one port match the criteria.

    Example:
    >>> find_port(hwid='USB VID:PID=2341:0043')
    '/dev/ttyACM0'
    """
    matching_ports = find_serial_ports(**kwargs)

    if len(matching_ports) == 1:
        return matching_ports[0]
    elif len(matching_ports) > 1:
        raise ValueError("More than one port found matching the criteria.")
    else:
        raise ValueError("No ports found matching the criteria.")

def serial_port_info(port_name):
    """
    Prints out all relevant information about a specified serial port.

    This function retrieves detailed information about the specified serial port and prints it
    as a dictionary. The information includes attributes available in the ListPortInfo object,
    such as device, name, description, hwid, vid, pid, serial_number, location, manufacturer,
    product, and interface.

    Parameters:
    port_name (str): The name of the serial port (e.g., "/dev/ttyACM0" on Linux or "COM3" on Windows).

    Example:
    >>> serial_port_info("/dev/ttyACM0")
    {
        'device': '/dev/ttyACM0',
        'name': 'ttyACM0',
        'description': 'Arduino Uno',
        'hwid': 'USB VID:PID=2341:0043',
        ...
    }
    """

    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.device == port_name:
            port_info = {attr: getattr(port, attr) for attr in dir(port) if not attr.startswith('__') and not callable(getattr(port, attr))}
            print(port_info)
            return

    print(f"No information found for port: {port_name}")