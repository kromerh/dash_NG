import serial
import serial.tools.list_ports

arduinoPort = '/dev/ttyACM0'  # might need to be changed if another arduino is plugged in or other serial


print([comport.device for comport in serial.tools.list_ports.comports()])