from pyModbusTCP.client import ModbusClient
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

db = pymysql.connect(host="twofast-RPi3-0",  # your host
					 user=user,  # username
					 passwd=pw,  # password
					 db="NG_twofast_DB", # name of the database
					 charset='utf8',
					 cursorclass=pymysql.cursors.DictCursor)

# MAC Address of the microwave generator
# MAC Address: 00:80:A3:C2:AB:65 (Lantronix)

# sudo
try:
	# c = ModbusClient(host="169.254.150.42", port=502, auto_open=True, auto_close=True)
	c = ModbusClient(host="169.254.240.116", port=502, auto_open=True, auto_close=True)
	# c = ModbusClient(host="169.254.240.1", port=502, auto_open=True, auto_close=True)
except ValueError:
	print("Error with host or port params")


def save_power_to_DB(FP, RP, power_setpoint):
	# Create a Cursor object to execute queries.
	cur = db.cursor()
	try:
		cur.execute("""INSERT INTO microwave_generator_power (FP, RP, power_setpoint) VALUES (%(FP)s, %(RP)s, %(power_setpoint)s)""" % {"FP": FP, "RP": RP, "power_setpoint": power_setpoint})
	except:
		cur.rollback()

	db.commit()
	cur.close()

def save_freq_to_DB(frequency, frequency_setpoint):
	# Create a Cursor object to execute queries.
	cur = db.cursor()
	try:
		cur.execute("""INSERT INTO microwave_generator_frequency (frequency, frequency_setpoint) VALUES (%(frequency)s, %(frequency_setpoint)s)""" % {"frequency": frequency, "frequency_setpoint": frequency_setpoint})
	except:
		cur.rollback()

	db.commit()
	cur.close()

def save_status_to_DB(status):
	print(status)
	# Create a Cursor object to execute queries.
	cur = db.cursor()
	try:
		cur.execute("""INSERT INTO microwave_generator_state (status) VALUES (%(status)s)""" % {"status": status})
	except:
		cur.rollback()

	db.commit()
	cur.close()


# bool to store if all the settings are set
RAMP_SET = False
RAMP_TIME_SET = False
FP_SET = False
RP_SET = False
MODE_SET = False
MW_ON = False
FREQ_SET = False

FREQUENCY_SETPOINT = 24400

def send_heartbeat(ModbusClient):
	# sends MODBUS heart beat
	# c is ModbusClient
	wr = ModbusClient.write_single_register(20, 128) # modbus heartbeat

def set_start_mode_ramp(ModbusClient):
	# Sets the start mode to ramp
	# c is ModbusClient
	wr = ModbusClient.write_single_register(3,2)
	# print('set_start_mode_ramp:' + str(int(wr)))
	return wr

def set_start_time(ModbusClient):
	# Sets the start time to 60s
	# c is ModbusClient
	wr = ModbusClient.write_single_register(4,60)
	print('set_start_time:' + str(int(wr)))
	return wr

def set_FW_power(ModbusClient):
	# Sets the forward power set point to 200 W
	# c is ModbusClient
	wr = ModbusClient.write_single_register(0,200)
	# print('set_FW_power:' + str(int(wr)))
	return wr

def set_RP(ModbusClient):
	# Sets the reflected power set point to 100 W
	# c is ModbusClient
	wr = ModbusClient.write_single_register(1,100)
	# print('set_RP:' + str(int(wr)))
	return wr

def set_freq(ModbusClient):
	# Sets the frequency before the autotuning
	# c is ModbusClient
	wr = ModbusClient.write_single_register(9,FREQUENCY_SETPOINT)
	# print('set_freq:' + str(int(wr)))
	return wr

def set_microwave_mode(ModbusClient):
	# Sets the microwave mode:
	#	autotuning on, reflected power RP limitation, reset faults
	# c is ModbusClient
	bit_addr = 2
	bit_value = 146 # 0 1 0 0 1 0 0 1
	wr = c.write_single_register(bit_addr, bit_value)
	# print('set_microwave_mode:' + str(int(wr)))
	return wr

def set_microwave_ON(ModbusClient):
	# Sets the microwave mode:
	#	autotuning on, reflected power RP limitation, MW ON, reset faults
	# c is ModbusClient
	bit_addr = 2
	bit_value = 210 # 0 1 0 0 1 0 1 1
	wr = c.write_single_register(bit_addr, bit_value)
	# print('set_microwave_ON:' + str(int(wr)))
	return wr



def read_fault_present(ModbusClient):
	# reads if fault present
	r0 = c.read_holding_registers(104, 1)
	r1 = c.read_holding_registers(105, 1)

	return [r0[0], r1[0]]

def read_FP(ModbusClient):
	# reads forward power
	r0 = c.read_holding_registers(102, 1)
	# print('read_FP :')
	# print(r0)
	return r0

def read_RP(ModbusClient):
	# reads reflected power
	r0 = c.read_holding_registers(103, 1)
	# print('read_RP:')
	# print(r0[0])
	return r0

def read_set_FP(ModbusClient):
	# reads setpoint power
	r0 = c.read_holding_registers(100, 1)
	# print('read_set_FP')
	# print(r0)
	return r0

def read_freq(ModbusClient):
	# reads current frequency
	r0 = c.read_holding_registers(112, 1)
	# print('read_freq:')
	# print(r0)
	return r0



while True:
	# sent hearbeat
	send_heartbeat(c)

	# set start mode to tamp
	if RAMP_SET == False:
		RAMP_SET = set_start_mode_ramp(c)

	# set start time 60 s
	if RAMP_TIME_SET == False:
		RAMP_TIME_SET = set_start_time(c)

	# set the forward power set point to 200 W
	if FP_SET == False:
		FP_SET = set_FW_power(c)

	# set the reflected power set point to 100 W
	if RP_SET == False:
		RP_SET = set_RP(c)

	# set the reflected power set point to 100 W
	if FREQ_SET == False:
		FREQ_SET = set_freq(c)

	# set the microwave mode:
	if MODE_SET == False:
		 MODE_SET = set_microwave_mode(c)

	status = read_fault_present(c)
	forward_power = read_FP(c)
	reflected_power = read_RP(c)
	setpoint_power = read_set_FP(c)
	frequency_read = read_freq(c)


	# set the microwaves ON:
	if MW_ON == False:
		MW_ON = set_microwave_ON(ModbusClient)

	print(status, forward_power, reflected_power, setpoint_power, frequency_read)

	# save to DB
	save_power_to_DB(forward_power[0], reflected_power[0], setpoint_power[0])
	save_freq_to_DB(frequency_read[0], FREQUENCY_SETPOINT/10)

	status.insert(0, '104:')
	status.insert(2, ', 105:')
	status = [str(s) for s in status]
	save_status_to_DB(' '.join(status))

# while True:
# 	set_microwave_mode(c)

# while True:
# 	wr = c.write_single_register(20, 128) # modbus heartbeat
# 	rr = c.read_holding_registers(99, 1)
# 	r0 = c.read_holding_registers(105, 1)
# 	print(r0)

# addr = 104
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)

# addr = 108
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)


# addr = 102
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)

