from time import sleep
import time
import datetime
import serial
import sys
import pandas as pd
import sqlalchemy as sql
import re

master_mode = 'testing'
# master_mode = 'operation'

readline_buffer = 500


# *****************
# SERIAL CONNECTION
# *****************

# Serial connection to the microwave generator
microwavePort = '/dev/ttyACM0' # NOT THIS ONE probably. check with /dev/tty* before and after connecting the microwave generator
if master_mode == 'testing':
	print('Testing: serial.Serial(microwavePort, 115200)')
else:
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

host="twofast-RPi3-0",  # your host
user=user  # username
passwd=pw  # password
db="NG_twofast_DB" # name of the database
connect_string = 'mysql://%(user)s:%(pw)s@%(host)s/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)

# truncate the command table
sql_engine.execute("TRUNCATE TABLE microwave_generator_command")



def getCommandsToExecute(sql_engine):
	"""
	Get the last 5 commands that were not executed. Returns the dataframe
	"""
	query = "SELECT * FROM microwave_generator_command WHERE executed = 0 ORDER BY time_created ASC LIMIT 5"
	df = pd.read_sql(query, sql_engine)

	if master_mode == 'testing':
		print('Testing: getCommandsToExecute, dataframe is:')
		print(df)

	# columns: time_created (timestamp), time_executed (timestamp), command (text), executed (1 or 0), id (primary key)
	return df


def updateCommandAsExecuted(command_id, timeNow, answer, sql_engine):
	"""
	After the command was sent to the microwave generator (and no error returned), update in the database that the command has been sent.
	answer: response from the microwave generator
	"""
	timeExecuted = timeNow.strftime('%Y-%m-%d %H:%M:%S')
	sql_engine.execute("UPDATE microwave_generator_command SET executed = 1, time_executed = '%(time)s', answer = %(answer)s WHERE id = %(commandId)s" % {"time": timeExecuted, "commandId": command_id, "answer": answer})



def switchDLLstateInControlTable(sql_engine):
	timeExecuted = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	sql_engine.execute("UPDATE microwave_generator_control SET DLL_on = 1 - DLL_on, time = '%(timeExecuted)s' WHERE id = 1" % {"timeExecuted": timeExecuted})


def sendCommandToMicrowave(command, ser, command_id, sql_engine, readline_buffer=500):
	"""
	Takes one command and the serial connection to the microwave generator as input and sends command via serial to the microwave.
	command: is the full command
	ser: serial connection to microwave generator
	command_id: id of the command in the microwave_generator_command table
	readline_buffer: default is 500, how much to read from the serial
	"""

	# send the command
	cmd = command
	if master_mode == 'testing':
		print('Testing inside sendCommandToMicrowave: ser.write(cmd.encode())')
	else:
		ser.write(cmd.encode())

	# sleep 0.01 s
	sleep(0.01)

	# get answer
	if master_mode == 'testing':
		print('Testing inside sendCommandToMicrowave: response = str(ser.readline(readline_buffer))')
	else:
		response = str(ser.readline(readline_buffer))
	print('Response when sending command %(cmd)s is %(response)s' % {"cmd": cmd, "response": response})

	# call updateCommandAsExecuted(command_id, timeExecuted, answer) to update executed to 1 and store answer from the microwave generator
	timeNow = datetime.datetime.now()
	updateCommandAsExecuted(command_id, timeNow, response, sql_engine)


	# if the command is to turn the DLL_on, update the control table
	if ('DLL' in cmd) & ('OK' in response):
		# toggle the DLL_on column value in the control table
		switchDLLstateInControlTable(sql_engine)


def insertMicrowaveReadoutIntoTable(frequency_soll, power_soll, temp1, temp2, relais_5, relais_24, rf_status, power_out, power_reflected, DLL_frequency, DLL_reflexion, sql_engine):
	if float(frequency_soll) > -1:
		sql_engine.execute("INSERT INTO microwave_generator_frequency (frequency) VALUES (%(val)s)" % {"val": frequency_soll})
	if float(power_soll) > -1:
		sql_engine.execute("INSERT INTO microwave_generator_power (power) VALUES (%(val)s)" % {"val": power_soll})
	if (float(temp1) > -1) & (float(temp2) > -1):
		sql_engine.execute("INSERT INTO microwave_generator_temperature (temperature1, temperature2) VALUES (%(val1)s, %(val2)s)" % {"val1": temp1, "val2": temp2})
	if float(relais_5) > -1:
		sql_engine.execute("INSERT INTO microwave_generator_state (relais_5) VALUES (%(relais_5)s)" % {"relais_5": relais_5})
	if float(relais_24) > -1:
		sql_engine.execute("INSERT INTO microwave_generator_state (relais_24) VALUES (%(relais_24)s)" % {"relais_24": relais_24})
	if float(rf_status) > -1:
		sql_engine.execute("INSERT INTO microwave_generator_state (rf_status) VALUES (%(rf_status)s)" % {"rf_status": rf_status})
	if (float(power_out) > -1) & (float(power_reflected) > -1):
		sql_engine.execute("INSERT INTO microwave_generator_reflected_power (power_out, power_reflected) VALUES (%(power_out)s, %(power_reflected)s)" % {"power_out": power_out, "power_reflected": power_reflected})
	if (float(DLL_frequency) > -1) & (float(DLL_reflexion) > -1):
		sql_engine.execute("INSERT INTO microwave_generator_DLL (DLL_frequency, DLL_reflexion) VALUES (%(DLL_frequency)s, %(DLL_reflexion)s)" % {"DLL_frequency": DLL_frequency, "DLL_reflexion": DLL_reflexion})



def insertIntoDLLTable(DLL_frequency, DLL_reflexion, sql_engine):
	sql_engine.execute("UPDATE microwave_generator_DLL SET DLL_frequency = %(DLL_frequency)s, DLL_reflexion = %(DLL_reflexion)s" % {"DLL_frequency": DLL_frequency, "DLL_reflexion": DLL_reflexion})



def readMicrowave(ser, mode='normal', readline_buffer=500):
	"""
	Reads the microwave generator.
	ser: serial connection
	mode: {
			'normal': frequency_soll, power_soll, temp1 and temp2, relais_5, relais_24, rf_status, power_out, power_reflected
			}
	readline_buffer: default is 500, how much to read from the serial
	"""
	# initialize everything as -1
	frequency_soll = -1
	power_soll = -1
	temp1 = -1
	temp2 = -1
	relais_5 = -1
	relais_24 = -1
	rf_status = -1
	power_out = -1
	power_reflected = -1
	DLL_frequency = -1
	DLL_reflexion = -1

	# send read command frequency_soll: $FRQG
	cmd = '$FRQG'
	if master_mode == 'testing':
		print('Testing inside readMicrowave: ser.write(cmd.encode()) cmd=' + cmd)
	else:
		ser.write(cmd.encode())

	# sleep 0.01 s
	sleep(0.01)

	# read serial, will return $FRQG:2450MHz
	if master_mode == 'testing':
		print('Testing inside readMicrowave: str(ser.readline(readline_buffer)) cmd=' + cmd)
		response = '$FRQG:2450MHz'
	else:
		response = str(ser.readline(readline_buffer))
	t_ = re.findall(r':(\d+)', response)
	print('frequency_soll response: {response}')

	# extract the frequency from the response and if it is the good one, send it to the database
	if (len(t_) > 0) & (cmd in response):
		frequency_soll = t_[0]
	else:
		print('ERROR frequency_soll response: {response}')




	# send read command power_soll: $PWRG
	cmd = '$PWRG'
	if master_mode == 'testing':
		print('Testing inside readMicrowave: ser.write(cmd.encode()) cmd=' + cmd)
	else:
		ser.write(cmd.encode())

	# sleep 0.01 s
	sleep(0.01)

	# read serial, will return $PWRG:250.2W
	if master_mode == 'testing':
		print('Testing inside readMicrowave: str(ser.readline(readline_buffer)) cmd=' + cmd)
		response = '$PWRG:250.2W'
	else:
		response = str(ser.readline(readline_buffer))
	t_ = re.findall(r':(.+)W', response)
	print('power_soll response: {response}')

	if (len(t_) > 0) & (cmd in response):
		power_soll = t_[0]
	else:
		print('ERROR power_soll response: {response}')


	# send read command temp1 and temp2: $TMPG
	cmd = '$TMPG'
	if master_mode == 'testing':
		print('Testing inside readMicrowave: ser.write(cmd.encode()) cmd=' + cmd)
	else:
		ser.write(cmd.encode())

	# sleep 0.01 s
	sleep(0.01)

	# read serial, will return $TMPG:19oC,20oC
	if master_mode == 'testing':
		print('Testing inside readMicrowave: str(ser.readline(readline_buffer)) cmd=' + cmd)
		response = '$TMPG:19oC,20oC'
	else:
		response = str(ser.readline(readline_buffer))
	print('temp1 response: {response}')

	t_ = re.findall(r':(\d+).*[^0-9](\d+)', response)

	if (len(t_) > 1) & (cmd in response):
		temp1 = t_[0]
		temp2 = t_[1]
	else:
		print('ERROR temp1 response: {response}')



	# send read command relais_5: $FVRG
	cmd = '$FVRG'
	if master_mode == 'testing':
		print('Testing inside readMicrowave: ser.write(cmd.encode()) cmd=' + cmd)
	else:
		ser.write(cmd.encode())


	# sleep 0.01 s
	sleep(0.01)

	# read serial, will return $FVRG:1 (activated) or $FVRG:0 (deactivated)
	if master_mode == 'testing':
		print('Testing inside readMicrowave: str(ser.readline(readline_buffer)) cmd=' + cmd)
		response = '$FVRG:1'
	else:
		response = str(ser.readline(readline_buffer))
	print('relais_5 response: {response}')

	t_ = re.findall(r':(\d+)', response)

	if (len(t_) > 0) & (cmd in response):
		relais_5 = t_[0]
	else:
		print('ERROR relais_5 response: {response}')


	# send read command relais_24: $PLRG
	cmd = '$PLRG'
	if master_mode == 'testing':
		print('Testing inside readMicrowave: ser.write(cmd.encode()) cmd=' + cmd)
	else:
		ser.write(cmd.encode())

	# sleep 0.01 s
	sleep(0.01)

	# read serial, will return $PLRG:1 (activated) or $PLRG:0 (deactivated)
	if master_mode == 'testing':
		print('Testing inside readMicrowave: str(ser.readline(readline_buffer)) cmd=' + cmd)
		response = '$PLRG:1'
	else:
		response = str(ser.readline(readline_buffer))
	print('relais_24 response: {response}')

	t_ = re.findall(r':(\d+)', response)

	if (len(t_) > 0) & (cmd in response):
		relais_24 = t_[0]
	else:
		print('ERROR relais_24 response: {response}')



	# send read command rf_status: $ENAG
	cmd = '$ENAG'
	if master_mode == 'testing':
		print('Testing inside readMicrowave: ser.write(cmd.encode()) cmd=' + cmd)
	else:
		ser.write(cmd.encode())

	# sleep 0.01 s
	sleep(0.01)

	# read serial, will return $ENAG:1 (activated) or $ENAG:0 (deactivated)
	if master_mode == 'testing':
		print('Testing inside readMicrowave: str(ser.readline(readline_buffer)) cmd=' + cmd)
		response = '$ENAG:1'
	else:
		response = str(ser.readline(readline_buffer))
	print('rf_status response: {response}')

	t_ = re.findall(r':(\d+)', response)

	if (len(t_) > 0) & (cmd in response):
		rf_status = t_[0]
	else:
		print('ERROR rf_status response: {response}')




	# send read command power_out and power_reflected: $FRPG
	cmd = '$FRPG'
	if master_mode == 'testing':
		print('Testing inside readMicrowave: ser.write(cmd.encode()) cmd=' + cmd)
	else:
		ser.write(cmd.encode())

	# sleep 0.01 s
	sleep(0.1)

	# read serial, will return $FRPG:120.0W,24.2W
	if master_mode == 'testing':
		print('Testing inside readMicrowave: str(ser.readline(readline_buffer)) cmd=' + cmd)
		response = '$FRPG:120.0W,24.2W'
	else:
		response = str(ser.readline(readline_buffer))
	print('power_out, power_reflected response: {response}')

	t_ = re.findall(r':(\d+\.\d)W,(\d+\.\d)W', response)

	if (len(t_) > 1) & (cmd in response):
		power_out = t_[0]
		power_reflected = t_[1]

	else:
		print('ERROR power_out, power_reflected response: {response}')


	# check if the DLL is on or off
	query = "SELECT DLL_on FROM `microwave_generator_control` WHERE id = 1"
	df = pd.read_sql(query, sql_engine)
	DLL_on = df['DLL_on'].values[0]

	if DLL_on == 1:

		cmd = '$DLE'
		if master_mode == 'testing':
			print('Testing inside readMicrowave: ser.write(cmd.encode()) cmd=' + cmd)
		else:
			ser.write(cmd.encode())

		# sleep 0.01 s
		sleep(0.1)

		# read serial, will return DLL_frequency, DLL_reflexion $DLE,2449,-2.18dB
		if master_mode == 'testing':
			print('Testing inside readMicrowave: str(ser.readline(readline_buffer)) cmd=' + cmd)
			response = '$DLE:2449,-2.18dB'
		else:
			response = str(ser.readline(readline_buffer))
		print('DLL_frequency, DLL_reflexion response: {response}')

		t_ = re.findall(r',(\d+),(.*\.\d+)dB', response)


		if (len(t_) > 1) & (cmd in response):
			DLL_frequency = t_[0]
			DLL_reflexion = t_[1]

		else:
			print('ERROR DLL_frequency, DLL_reflexion response: {response}')

	insertMicrowaveReadoutIntoTable(frequency_soll, power_soll, temp1, temp2, relais_5, relais_24, rf_status, power_out, power_reflected, DLL_frequency, DLL_reflexion, sql_engine)


while True:
	try:
		sleep(0.2) # sleep mind. 200 ms, 1/250 ms is the maximal readout frequency that the microwave generator can handle

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
				# def sendCommandToMicrowave(command, ser, command_id, sql_engine, readline_buffer=500)
				sendCommandToMicrowave(cmd, ser, cmd_id, sql_engine, readline_buffer)


		# read the microwave generator
		readMicrowave(ser, 'normal', readline_buffer)
		if master_mode == 'operation':
			ser.flushInput()  #flush input buffer, discarding all its contents
			ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
	except KeyboardInterrupt:
		print('Ctrl + C. Exiting. Flushing serial connection.')
		if master_mode == 'operation':
			ser.flushInput()  #flush input buffer, discarding all its contents
			ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
		sys.exit(1)