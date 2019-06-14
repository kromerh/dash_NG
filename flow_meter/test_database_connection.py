from time import sleep
import serial
import sys
import pandas as pd
import pymysql

mysql_connection = pymysql.connect(host="twofast-RPi3-0",  # your host
					 user="writer",  # username
					 passwd="heiko",  # password
					 db="NG_twofast_DB", # name of the database
					charset='utf8',
					cursorclass=pymysql.cursors.DictCursor)

def getFlowMeterControlValues(mysql_connection):
	# DOSE
	query = "SELECT * FROM flow_meter_control"
	print(df.loc['setpoint_voltage'].values)

	return df



print(getFlowMeterControlValues(mysql_connection))

sys.exit()



arduinoPort = '/dev/ttyACM0'
ser = serial.Serial(arduinoPort, 9600)
sleep(1)
val = 0.5 # Below 32 everything in ASCII is gibberish
while True:
	try:
		valueSend = str(val)
		ser.write(valueSend.encode()) # Convert the decimal number to ASCII then send it to the Arduino
		print(valueSend.encode())
		sleep(1) # Delay
		valueRead = ser.readline(500)

		print(valueRead) # Read the newest output from the Arduino
		sleep(0.5) # Delay
		ser.flushInput()  #flush input buffer, discarding all its contents
		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
	except KeyboardInterrupt:
		print('Ctrl + C. Exiting. Flushing serial connection.')
		ser.flushInput()  #flush input buffer, discarding all its contents
		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
		sys.exit(1)