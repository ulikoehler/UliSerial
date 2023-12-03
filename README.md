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

## License

See [LICENSE](LICENSE) file.