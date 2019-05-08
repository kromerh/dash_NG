import serial
from time import sleep
import sys

arduinoPort = '/dev/ttyACM0'
ser = serial.Serial(arduinoPort, 9600)

def pi_read():
	ser = serial.Serial(arduinoPort, 9600)
	while (ser.inWaiting() == 0):  # wait for incoming data
		pass
	valueRead = ser.readline(500)
	try:
		valueRead = (valueRead.decode('utf-8')).strip()
	# print(valueRead)
	except UnicodeDecodeError:
		valueRead = '-1'
	return valueRead

while True:
	try:
		print("writing")
		ser.write(b'21')
		sleep(1)

		# Read the incoming data
		incoming_data = pi_read()
		print(incoming_data)
		sleep(0.1)
	except KeyboardInterrupt:
		print('Ctrl + C. Exiting. Flushing serial connection.')
		ser.flushInput()  #flush input buffer, discarding all its contents
		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
		sys.exit(1)
