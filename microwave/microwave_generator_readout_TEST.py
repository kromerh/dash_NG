from time import sleep
import time
import datetime
import serial
import sys
import pandas as pd
import sqlalchemy
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
