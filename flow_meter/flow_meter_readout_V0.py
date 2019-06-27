from time import sleep
import serial
import sys
import pandas as pd
import pymysql
import re

# read password and user to database
credentials_file = r'./credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]

def getFlowMeterControlValues():
	# DOSE
	mysql_connection = pymysql.connect(host="twofast-RPi3-0",  # your host
					 user=user,  # username
					 passwd=pw,  # password
					 db="NG_twofast_DB", # name of the database
					 charset='utf8',
					 cursorclass=pymysql.cursors.DictCursor)

	query = "SELECT * FROM flow_meter_control"
	df = pd.read_sql(query, mysql_connection)

	setpoint_voltage = df.loc[:,'setpoint_voltage'].values[0]

	# print(setpoint_voltage)

	return setpoint_voltage


db = pymysql.connect(host="twofast-RPi3-0",  # your host
					 user=user,  # username
					 passwd=pw,  # password
					 db="NG_twofast_DB", # name of the database
					 charset='utf8',
					 cursorclass=pymysql.cursors.DictCursor)

arduinoPort = '/dev/ttyACM0'  # might need to be changed if another arduino is plugged in or other serial

def saveFlowMeterVoltageToDB(voltage):
	# Create a Cursor object to execute queries.
	cur = db.cursor()
	try:
		cur.execute("""INSERT INTO flow_meter_readout_live (read_voltage) VALUES (%s)""", (voltage))
	except:
		cur.rollback()

	db.commit()
	cur.close()


ser = serial.Serial(arduinoPort, 9600)
print('Serial connected at ' + str(arduinoPort))
sleep(1)
# val = 0.5 # Below 32 everything in ASCII is gibberish
while True:
	try:
		# SETPOINT VALUE OF FLOW METER
		# read the database for the setpoint value
		setpoint_voltage = getFlowMeterControlValues()

		# convert
		valueSend = str(setpoint_voltage)
		# print("Sending value to Arduino " + valueSend)
		# send
		ser.write(valueSend.encode()) # Convert the decimal number to ASCII then send it to the Arduino

		print("Successfully sent to Arduino:" + str(valueSend.encode()))

		sleep(0.5) # Delay

		# READING OF FLOW METER
		valueRead = ser.readline(500) # b'V_1 1.30, 4.20, V_out 215.04\r\n'

		print('Raw reading from Arduino :' + str(valueRead)) # Read the newest output from the Arduino
		voltageStr = str(valueRead).split(',')

		voltageStr = voltageStr[0]



		t = re.findall(r'V_1 (.+)', voltageStr)

		if len(t) > 0:
			voltage = t[0]
			# print(voltage)
			saveFlowMeterVoltageToDB(voltage) # save into DB

		sleep(0.5) # Delay
		ser.flushInput()  #flush input buffer, discarding all its contents
		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
	except KeyboardInterrupt:
		print('Ctrl + C. Exiting. Flushing serial connection.')
		ser.flushInput()  #flush input buffer, discarding all its contents
		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
		sys.exit(1)