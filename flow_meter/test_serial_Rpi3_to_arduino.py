import serial  # Importing the serial library to communicate with Arduino
import serial.tools.list_ports
from time import sleep # Importing the time library to provide the delays in program
import re
import sys

# ser = serial.Serial('/dev/ttyACM0', 9600) 
V_setpoint = 2  # THIS MUST BE A STRING

def read_serial_ports():
    """
    Reads the available serial ports, returning a lsit
    """
    return list(serial.tools.list_ports.comports())

def pi_flush(serial_port):
    serialArduino = serial.Serial(port=serial_port, baudrate=9600)
    serialArduino.flushInput()  #flush input buffer, discarding all its contents
    serialArduino.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer

def pi_write(serial_port, V_setpoint):
    """
    Sets the setpoint voltage, sending it to the Arduino.
    """
    serialArduino = serial.Serial(port=serial_port, baudrate=9600)
    V_setpoint = b'%d' %V_setpoint
    serialArduino.write(V_setpoint) # Sending data to the Arduino, ranges from 0 to 255 (0 to 5 Volt)
    print(V_setpoint)

def pi_read(serial_port):
    """
    Sets the setpoint voltage, sending it to the Arduino.
    Reads the serial port and returns what it reads. 
    """
    serialArduino = serial.Serial(port=serial_port, baudrate=9600)
    while (serialArduino.inWaiting() == 0):  # wait for incoming data
        pass

    valueRead = serialArduino.readline(500)

    try:
        valueRead = (valueRead.decode('utf-8')).strip()
       # print(valueRead)
    except UnicodeDecodeError:
        valueRead = '-1'
    return valueRead

arduinoPort = '/dev/ttyACM0'

# ports = read_serial_ports()
# for port in ports:
#     t = re.findall(r'(/dev/\S+).+Arduino', str(port))
#     print(port)
#     if len(t) > 0:
#         arduinoPort = t[0]
#         print('Arduino port found: ', str(port))
#         break

if arduinoPort == None:
    print('No Arduino connected on serial port. Exiting.')
    sys.exit(1)

while True:
    try:
        # Read the incoming data
        pi_write(arduinoPort, V_setpoint)
        sleep(0.1)
        incoming_data = pi_read(arduinoPort)
        print(incoming_data)
        sleep(0.1)
    except KeyboardInterrupt:
        print('Ctrl + C. Exiting. Flushing serial connection.')
        pi_flush(arduinoPort)
        sys.exit(1)
    finally:
        pi_flush(arduinoPort)
