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

host="twofast-rpi3-0"  # your host
user=user # username
passwd=pw  # password
db="NG_twofast_DB" # name of the database
connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}

sql_engine = sql.create_engine(connect_string)

# truncate the command table
sql_engine.execute("TRUNCATE TABLE microwave_generator_command")


sql_engine.execute("INSERT INTO microwave_generator_control (command, executed) VALUES ('a 1 test', 0)")

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

df_commands = getCommandsToExecute(sql_engine)

print(df_commands)