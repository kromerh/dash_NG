from time import sleep
import time
import datetime
import serial
import sys
import pandas as pd
import sqlalchemy as sql
import re

# *****************
# SERIAL CONNECTION
# *****************

# Serial connection to the microwave generator
arduinoPort = '/dev/ttyACM0' # NOT THIS ONE probably. check with /dev/tty* before and after connecting the microwave generator

ser = serial.Serial(arduinoPort, 9600) 

print('Connected to Arduino on ' + arduinoPort + 'baudrate 9600')

sleep(0.1)  # sleep to connect to microwave generator

# *****************
# DATABASE
# *****************

# read password and user to database
credentials_file = r'/home/pi/credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]

host="twofast-RPi3-0"  # your host
user=user  # username
passwd=pw  # password
db="NG_twofast_DB" # name of the database
connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)


def getCommandsToExecute(sql_engine):
	"""
	Get the commands from the motor control table
	"""
	query = "SELECT * FROM microwave_motor_command WHERE executed = 0 ORDER BY time_created ASC LIMIT 5"
	df = pd.read_sql(query, sql_engine)


	# columns: time_created (timestamp), time_executed (timestamp), command (text), executed (1 or 0), id (primary key)
	return df


def updateCommandAsExecuted(command_id, timeNow, sql_engine):
	"""
	After the command was sent to the motor, it is updated as having executed.
	"""
	timeExecuted = timeNow.strftime('%Y-%m-%d %H:%M:%S')
	sql_engine.execute("UPDATE microwave_motor_command SET executed = 1, time_executed = '%(time)s' WHERE id = %(commandId)s" % {"time": timeExecuted, "commandId": command_id})


def sendCommandToMotor(command, command_id):
	"""
	Sends a command to the motor.
	"""
	# convert command
	valueSend = str(command)
	# print("Sending value to Arduino " + valueSend)
	# send
	ser.write(valueSend.encode()) # Convert the decimal number to ASCII then send it to the Arduino
	print("Sent to Arduino:" + str(valueSend.encode()))
	sleep(0.5) # Delay
	# update as command having executed, this assumes that sending to the Arduino is equivalent to it being executed.
	timeNow = datetime.datetime.now()
	updateCommandAsExecuted(command_id, timeNow, sql_engine)


while True:
	try:
		sleep(0.2) # sleep 200 ms

		# read the list of not executed commands from the database
		df_commands = getCommandsToExecute(sql_engine)

		# if there are some commands to execute, send them all to the microwave generator
		if len(df_commands) > 0:

			# loop over all the rows to execute the commands line by line
			for index, row in df.iterrows():

				# get command from the row, convert to string just to be sure
				cmd = str(row['command'])

				# get id of that command from the row, convert to string just to be sure
				cmd_id = str(row['id'])

				# send the command, in there it also updates the time and sets executed to 1
				sendCommandToMotor(cmd, cmd_id)

	except KeyboardInterrupt:
		print('Ctrl + C. Exiting. Flushing serial connection.')
		if master_mode == 'operation':
			ser.flushInput()  #flush input buffer, discarding all its contents
			ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
		sys.exit(1)