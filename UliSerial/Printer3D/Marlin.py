#!/usr/bin/env python3
import queue
import time
import serial
import serial.threaded
import traceback
from collections import namedtuple
from typing import Dict

# NOTE: setpoint may be None
Temperature = namedtuple("Temperature", ["timestamp", "actual", "setpoint"])
Position = namedtuple("Position", ["timestamp", "value", "steps"])
Report = namedtuple("Report", ["timestamp", "line"])

class MarlinProtocol(serial.threaded.LineReader):
    """
    Implements basic features for a serial protocol for Marlin printers
    NOTE: At the moment, this is no full-featured implementation, but it can easily be extended
    """
    TERMINATOR = b'\n'
    
    def __init__(self):
        super().__init__()
        self.responses = queue.Queue(32768)
        # Last temperatures as reported by the printer. Key is "T", "B" etc - whatever the printer reports
        self.temperatures: Dict[str, Temperature] = {}
        self.positions: Dict[str, Position] = {}
        self.last_temperature_report: Report = None # Raw data of last temperature report
        self.last_position_report: Report = None # Raw data of last position report

    def stop(self):
        """
        Stop the event processing thread, abort pending commands, if any.
        """
        self.alive = False
        self.events.put(None)
        self.responses.put('<exit>')
    
    def handle_line(self, line):
        """
        Handle input from serial port, check for events.
        """
        line = line.strip()
        if not line: # Ignore empty lines
            return
        try:
            if line.startswith("ok"):
                self.responses.put(line)
            elif line.startswith("T"):
                self.parse_temperature_report(line)
            elif line.startswith("X"):
                positions = self.parse_position_report(line)
            else:
                print("Unknown line from printer: ", line)
        except:
            traceback.print_exc()
            print("Error parsing line from printer: ", line)
            
            
    def parse_position_report(self, line):
        """
        Parse a position report line such as
        X:101.00 Y:0.00 Z:0.00 E:0.00 Count X:10100 Y:0 Z:0
        """
        t = time.time()
        # Save raw position report
        self.last_position_report = Report(t, line)
        # "Count" is the number of steps
        if "Count" in line:
            line, _, count = line.partition("Count")
            line = line.strip()
            count = count.strip()
        else:
            count = ""
            
        # Parse line (X,Y,Z,E, ...)
        values_mm = {}
        for part in line.split():
            part = part.strip()
            if not part: continue
            label, value = part.strip().partition(":")[::2]
            values_mm[label] = float(value)
        
        # Parse count (X,Y,Z,E, ...)
        values_steps = {}
        for part in count.split():
            part = part.strip()
            if not part: continue
            label, value = part.strip().partition(":")[::2]
            values_steps[label] = float(value)
            
        # Merge both dicts
        positions = {}
        for key in set(list(values_mm.keys()) + list(values_steps.keys())):
            positions[key] = Position(t, values_mm.get(key, None), values_steps.get(key, None))
        return positions
        
    def parse_temperature_report(self, line):
        """
        Parse a temperature report line such as
        T:20.38 /185.00 @:127
        """
        t = time.time()
        # NOTE: Line is e.g.
        # NOTE: We join the setpoint and the temp column for easier parsing
        line = line.replace(" /", "/")
        # Split into parts
        parts = line.split()
        # Set raw data
        self.last_temperature_report = Report(t, line)
        # Extract the individual temperatures
        for part in parts:
            # part is e.g. "T:20.38" or "T:20.38/185.00"
            label, value = part.partition(":")[::2]
            if "@" in label:
                # This is the PWM setpoint, which we currently ignore
                continue
            # With or without setpoint
            if "/" in value:
                actual, setpoint = value.split("/")
                actual = float(actual)
                setpoint = float(setpoint)
                self.temperatures[label] = Temperature(t, actual, setpoint)
            else: # No setpoint, such as ambient temperature
                actual = float(value)
                self.temperatures[label] = Temperature(t, actual, None)
        
    def send_command(self, command):
        self.write_line(command)
        
    def send_command_receive_response(self, command):
        self.send_command(command)
        return self.responses.get(timeout=30)
        
    def continous_temperature_reporting(self):
        return self.send_command_receive_response("M155S1")
    
    def disable_temperature_reporting(self):
        return self.send_command_receive_response("M155S0")
    
    def report_position(self):
        return self.send_command_receive_response("M114")
        
    def relative_motion(self):
        return self.send_command_receive_response("G91")

import threading

class MarlinPrinterThread(object):
    """
    Create a Marlin printer which runs in an asynchronous thread.
    This allows the serial IO to be run concurrently with other tasks.
    
    This class automatically enables & disables temperature reporting
    
    Usage: Either using "with"
    with MarlinPrinterThread(port) as printer:
        printer.send_command("M104 S0")
        printer.send_command("G0X5F100")
        
    Or using start() and stop()
    printer = MarlinPrinterThread(port)
    printer.start()
    """
    def __init__(self, port):
        if isinstance(port, str):
            self._ser = serial.Serial(port, 115200, timeout=1)
            self._close_serial_on_exit = True
        else: # Assume it's already a serial port
            self._ser = port
            self._close_serial_on_exit = False
        self.port = port
        self.printer = None # Will be set in start()
        self.thread = None
        self._stop_thread = False
        self.position_report_interval = 1.0
        
    def __enter__(self):
        self.start()
    
    def _thread_fn(self):
        # Enable temperature reporting
        self.printer.continous_temperature_reporting()
        while not self._stop_thread:
            self.printer.report_position() # Position will be saved to printer.positions
            time.sleep(self.position_report_interval)
        
    def start(self):
        if self.printer is None:
            reader_thread = serial.threaded.ReaderThread(self._ser, MarlinProtocol)
            self.printer = reader_thread.__enter__()
        
        self.thread = threading.Thread(target=self._thread_fn)
        self.thread.start()
        return self
        
    def stop(self):
        # Wait for thread to exit gracefully
        if self.thread is not None: # If thread was started
            self._stop_thread = True
            self.thread.join()
            self.thread = None
        if self.printer is not None:
            # Gracefully stop printer
            # Disable continous printer reporting
            self.printer.disable_temperature_reporting()
            # Stop & disconnect printer connection
            self.printer.__exit__()
            # Prevent accidental re-use
            self.printer = None
        if self._close_serial_on_exit and self._ser is not None:
            self._ser.close()
        
    def __exit__(self, *args, **kwargs):
        self.stop()
