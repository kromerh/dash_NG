import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash_daq import DarkThemeProvider as DarkThemeProvider
from dash.dependencies import Input, Output, State
import dash
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import pymysql
import sqlalchemy as sql

import time
from datetime import datetime

from app import app

# dictionary that relates the number of the motor with the number of the button on the microwave
# 'button': motor
d_motors = {
	'button_1': 3,
	'button_2': 1,
	'button_3': 2,
}

# read password and user to database
credentials_file = r'./credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]


host = "twofast-RPi3-0"  # your host
user = user  # username
passwd = pw  # password
db = "NG_twofast_DB" # name of the database
connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
try:
	sql_engine = sql.create_engine(connect_string)
except:
	print("Could not connect to DB")


def MWButtonControl(sql_engine, motor, value, runtime):
	timeNow = datetime.now()
	# arduino looks for val1, time1, val2, time2, val3, time3
	command = ["90,200", "90,200", "90,200"] # motor 1, motor 2, motor 3
	command[motor-1] = f'{value},{runtime}'
	value = ",".join(command)
	qry = "INSERT INTO microwave_motor_command (time_created, command, executed) VALUES (\"%(time)s\", \"%(value)s\", 0)" % {"time": timeNow, "value": value}
	print(qry)
	sql_engine.execute(qry)
	time.sleep(3)



# CALLBACKS

# # status of MW motor
# # Stop the microwave button
# @app.callback(
# 	Output("microwave-status-monitor", "value"),
# 	[Input("microwave-MW-button-off", "children")],
# 	[State("microwave-MW-button-on", "children")]
# )
# def mw_motor_status(status_off, status_on):
# 	status = (
# 	"-----------STATUS------------\n"
# 	+ "microwave-MW-button-off: " + str(status_off) + "\n"
# 	+ "microwave-MW-button-on: " + str(status_on) + "\n"
# 	)
# 	return status



## FORWARD



@app.callback(
	Output("mw-motor-1-fw-slow-state", "children"),
	[Input("btn-mw-motor-1-fw-slow", "n_clicks")]
)
def btn_mw_1_fw_slow(n_clicks):
	if n_clicks:
		btn = 1
		value = 88
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None

@app.callback(
	Output("mw-motor-2-fw-slow-state", "children"),
	[Input("btn-mw-motor-2-fw-slow", "n_clicks")]
)
def btn_mw_2_fw_slow(n_clicks):
	if n_clicks:
		btn = 2
		value = 88
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None

@app.callback(
	Output("mw-motor-3-fw-slow-state", "children"),
	[Input("btn-mw-motor-3-fw-slow", "n_clicks")]
)
def btn_mw_3_fw_slow(n_clicks):
	if n_clicks:
		btn = 3
		value = 92
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None


# TURN FAST BUTTONS

@app.callback(
	Output("mw-motor-1-fw-fast-state", "children"),
	[Input("btn-mw-motor-1-fw-fast", "n_clicks")]
)
def btn_mw_1_fw_fast(n_clicks):
	if n_clicks:
		btn = 1
		value = 80
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None

@app.callback(
	Output("mw-motor-2-fw-fast-state", "children"),
	[Input("btn-mw-motor-2-fw-fast", "n_clicks")]
)
def btn_mw_2_fw_fast(n_clicks):
	if n_clicks:
		btn = 2
		value = 80
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None

@app.callback(
	Output("mw-motor-3-fw-fast-state", "children"),
	[Input("btn-mw-motor-3-fw-fast", "n_clicks")]
)
def btn_mw_3_fw_fast(n_clicks):
	if n_clicks:
		btn = 3
		value = 100
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None



## REVERSE

@app.callback(
	Output("mw-motor-1-rv-slow-state", "children"),
	[Input("btn-mw-motor-1-rv-slow", "n_clicks")]
)
def btn_mw_1_rv_slow(n_clicks):
	if n_clicks:
		btn = 1
		value = 92
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None

@app.callback(
	Output("mw-motor-2-rv-slow-state", "children"),
	[Input("btn-mw-motor-2-rv-slow", "n_clicks")]
)
def btn_mw_2_rv_slow(n_clicks):
	if n_clicks:
		btn = 2
		value = 92
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None

@app.callback(
	Output("mw-motor-3-rv-slow-state", "children"),
	[Input("btn-mw-motor-3-rv-slow", "n_clicks")]
)
def btn_mw_3_rv_slow(n_clicks):
	if n_clicks:
		btn = 3
		value = 88
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None


# TURN FAST BUTTONS

@app.callback(
	Output("mw-motor-1-rv-fast-state", "children"),
	[Input("btn-mw-motor-1-rv-fast", "n_clicks")]
)
def btn_mw_1_rv_fast(n_clicks):
	if n_clicks:
		btn = 1
		value = 100
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None

@app.callback(
	Output("mw-motor-2-rv-fast-state", "children"),
	[Input("btn-mw-motor-2-rv-fast", "n_clicks")]
)
def btn_mw_2_rv_fast(n_clicks):
	if n_clicks:
		btn = 2
		value = 100
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None

@app.callback(
	Output("mw-motor-3-rv-fast-state", "children"),
	[Input("btn-mw-motor-3-rv-fast", "n_clicks")]
)
def btn_mw_3_rv_fast(n_clicks):
	if n_clicks:
		btn = 3
		value = 80
		time = 1000
		s = f'button_{btn}'
		motor = d_motors[s]
		print(f'Button {btn}, value {value}, motor {motor}, time {time}')

		MWButtonControl(sql_engine, motor, value, time)

		return None
