import serial
import serial.tools.list_ports

arduinoPort = '/dev/ttyACM0'  # might need to be changed if another arduino is plugged in or other serial


def fun_read_serial_ports():
    return list(serial.tools.list_ports.comports())

print(fun_read_serial_ports())