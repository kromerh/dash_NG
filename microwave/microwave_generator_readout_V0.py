from time import sleep
import time
import datetime
import serial
import sys
import pandas as pd
import pymysql
import re

# *****************
# SERIAL CONNECTION
# *****************

# Serial connection to the microwave generator
microwavePort = '/dev/ttyACM0' # NOT THIS ONE probably. check with /dev/tty* before and after connecting the microwave generator
ser = serial.Serial(microwavePort, 115200) # Baud 115200, Data Bits: 8, StopBits: 1, Parity: none, FlowControl: none
print('Connected to microwavePort')
sleep(0.1)  # sleep to connect to microwave generator

# *****************
# DATABASE
# *****************

# read password and user to database
credentials_file = r'./credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]

mysql_connection = pymysql.connect(host="twofast-RPi3-0",  # your host
				 user=user,  # username
				 passwd=pw,  # password
				 db="NG_twofast_DB", # name of the database
				 charset='utf8',
				 cursorclass=pymysql.cursors.DictCursor)



def getCommandsToExecute(mysql_connection):
	"""
	Get the last 10 commands that were not executed. Returns the dataframe
	"""
	query = "SELECT * FROM microwave_generator_control WHERE executed = 0 ORDER BY time_created ASC LIMIT 10"
	df = pd.read_sql(query, mysql_connection)

	# columns: time_created (timestamp), time_executed (timestamp), command (text), executed (1 or 0), id (primary key)
	return df



def updateCommandAsExecuted(command_id, timeExecuted):
	"""
	After the command was sent to the microwave generator (and no error returned), update in the database that the command has been sent.
	"""
	timeExecuted = timeExecuted.strftime('%Y-%m-%d %H:%M:%S')
	cur = db.cursor()
	try:
		cur.execute("UPDATE microwave_generator_control SET executed = 1, time_executed = %(time)s WHERE id = %(commandId)s" % {"time": timeExecuted, "commandId": command_id })
	except:
		cur.rollback()

	db.commit()
	cur.close()


def sendCommandToMicrowave(command, ser):
	"""
	Takes one command and the serial connection to the microwave generator as input and sends command via serial to the microwave.
	"""

	# send the command

	# print that it was sent

	# read answer and update it in the database

	# call updateCommandAsExecuted(command_id, timeExecuted) if successful

	# sleep 0.1 seconds


	pass


def readMicrowave(ser, mode='normal'):
	"""
	Reads the microwave generator.
	ser: serial connection
	mode: {
			'normal': frequency_soll, power_soll, temp1 and temp2, relais_5, relais_24V
			'reflected': 'normal' + power_out, power_reflected. MAXIMAL 1/250 ms this command!!!
			'DLE': 'normal' + DLL_frequency, DLL_reflexion
			}
	"""


	# send read command frequency_soll: $FRQG

	# sleep 0.01 s

	# read serial, will return $FRQG:2450MHz


	# send read command power_soll: $PWRG

	# sleep 0.01 s

	# read serial, will return $PWRG:250.2W


	# send read command temp1 and temp2: $TMPG

	# sleep 0.01 s

	# read serial, will return $TMPG:19oC,20oC


	# send read command relais_5: $FVRG

	# sleep 0.01 s

	# read serial, will return $FVRG:1 (activated) or $FVRG:0 (deactivated)


	# send read command relais_24: $PLRG

	# sleep 0.01 s

	# read serial, will return $PLRG:1 (activated) or $PLRG:0 (deactivated)



	# if reflected mode

	# send read command power_out and power_reflected: $FRQG

	# sleep 0.01 s

	# read serial, will return $FRQG:120.0W,24.2W


	# if DLE mode

	# send read command DLL_frequency, DLL_reflexion: $DLE

	# sleep 0.01 s

	# read serial, will return $DLE:,2451,-8.25dB





	pass

# val = 0.5 # Below 32 everything in ASCII is gibberish
while True:
	try:
		sleep(0.05) # sleep mind. 50 ms, 1/10 ms is the maximal readout frequency that the microwave generator can handle

		# read the list of not executed commands from the database
		df_commands = getCommandsToExecute(mysql_connection)

		# if there are some commands to execute, send them all to the microwave generator
		if len(df_commands) > 0:

			# loop over all the rows to execute the commands line by line
			for index, row in df.iterrows():

				# get command from the row, convert to string just to be sure
				cmd = str(row['command'])

				# send the command, in there it also updates the time and sets executed to 1
				sendCommandToMicrowave(cmd, ser)


		# read the microwave generator
		readMicrowave(ser, mode='normal')

		# SETPOINT VALUE OF FLOW METER
		# read the database for the setpoint value
		setpoint_voltage = getFlowMeterControlValues()

		# convert
		valueSend = str(setpoint_voltage)

		# send
		ser.write(valueSend.encode()) # Convert the decimal number to ASCII then send it to the Arduino

		print("Sending to Arduino:" + str(valueSend.encode()))

		sleep(0.5) # Delay

		# READING OF FLOW METER
		valueRead = ser.readline(500) # b'V_1 1.30, 4.20, V_out 215.04\r\n'

		print('Raw reading from Arduino:' + str(valueRead)) # Read the newest output from the Arduino
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