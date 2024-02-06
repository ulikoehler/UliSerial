# UliSerial
Serial port utilities to save time with your electronics project

## Installation

```bash
pip install UliSerial
```

## Example usage

This code finds & opens a specific serial port using `pyserial`.
If no port, or multiple ports are found, `NoSuchSerialPortException` or `MultipleSerialPortsException` is raised (both subclasses of `UliSerialException`).

```python
from UliSerial.Find import *
import serial

port = find_serial_port(product="Marlin USB Device", serial_number="01010A23535223934CF29A1EF5000007")
# port is now e.g. '/dev/ttyACM0'
# Open the port
ser = serial.Serial(port, 115200, timeout=1)
```

You can find the possible attributes for a given serial port using e.g.
```python
from UliSerial.Find import *

serial_port_info("/dev/ttyACM0")
```

This prints something like
```
{
 'description': 'STLINK-V3 - ST-Link VCP Ctrl',
 'device': '/dev/ttyACM0',
 'device_path': '/sys/devices/pci0000:00/0000:00:14.0/usb1/1-4/1-4.1/1-4.1:1.2',
 'hwid': 'USB VID:PID=0483:374E SER=003E002D3532511431333430 LOCATION=1-4.1:1.2',
 'interface': 'ST-Link VCP Ctrl',
 'location': '1-4.1:1.2',
 'manufacturer': 'STMicroelectronics',
 'name': 'ttyACM0',
 'pid': 14158,
 'product': 'STLINK-V3',
 'serial_number': '003E002D3532511431333430',
 'subsystem': 'usb',
 'usb_device_path': '/sys/devices/pci0000:00/0000:00:14.0/usb1/1-4/1-4.1',
 'usb_interface_path': '/sys/devices/pci0000:00/0000:00:14.0/usb1/1-4/1-4.1/1-4.1:1.2',
 'vid': 1155
}
```
All these attributes can be used as keyword arguments to `find_serial_port()`.

## License

See [LICENSE](LICENSE) file.
