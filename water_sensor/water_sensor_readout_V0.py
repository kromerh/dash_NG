from time import sleep
import serial
import sys
import pandas as pd
import pymysql
import re
import sqlalchemy as sql

# read password and user to database
credentials_file = r'./credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]

host="twofast-RPi3-0"  # your host
user=user  # username
passwd=pw  # password
db="NG_twofast_DB" # name of the database
connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)

# truncate the command table


arduinoPort = '/dev/ttyACM0'  # might need to be changed if another arduino is plugged in or other serial

def save_sensor_data_to_db(y, sql_engine):
	"""
	y: list of the flags of s1, s2, s3. 1 means no water, 0 means water
	"""
	sql_engine.execute("INSERT INTO water_sensor_data (s1, s2, s3) VALUES (%(v1)s, %(v2)s, %(v3)s)" % {"v1": y[0], "v2": y[1], "v3": y[2]})


ser = serial.Serial(arduinoPort, 9600)
print('Serial connected at ' + str(arduinoPort))
sleep(1)
# val = 0.5 # Below 32 everything in ASCII is gibberish
while True:
	try:

		# READING 
		valueRead = ser.readline(500) # b'V_1 1.30, 4.20, V_out 215.04\r\n'

		# print('Raw reading from Arduino :' + str(valueRead)) # Read the newest output from the Arduino
		y_vals = valueRead.decode().strip().split(',')  # s1, s2, s3
		y_vals = [str(float(y)) for y in y_vals]
		print(y_vals)
		if len(y_vals) > 0:
			save_sensor_data_to_db(y_vals, sql_engine) # save into DB

		sleep(0.1) # Delay
		ser.flushInput()  #flush input buffer, discarding all its contents
		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
	except KeyboardInterrupt:
		print('Ctrl + C. Exiting. Flushing serial connection.')
		ser.flushInput()  #flush input buffer, discarding all its contents
		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
		sys.exit(1)
