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

state_dic = {'state': "none"}

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

################################################################################################################################################
# function
################################################################################################################################################

# ********************
# FLOW METER
# ********************

def setFlowMeterControlValues(value, sql_engine):
	"""
	Sets the entry for the setpoint value in the database according to the user specified value
	"""
	query= "UPDATE flow_meter_control SET setpoint_voltage = %(setpoint_voltage)s" % {"setpoint_voltage": value}
	sql_engine.execute(query)

	print(f'Updated setpoint_voltage {value} in flow_meter_control table.')


def readFlowMeterVoltage(sql_engine, pastSeconds=60): # read past 60secs by default
	"""
	Read the flow meter voltage read from the database
	"""
	query = "SELECT * FROM flow_meter_readout_live ORDER BY id DESC LIMIT %(pastSeconds)s" % {"pastSeconds": pastSeconds}
	df = pd.read_sql(query, sql_engine)

	return df


################################################################################################################################################
# callbacks
################################################################################################################################################
# ********************************
# FLOW METER
# ********************************

# Start  the flow meter readout from the database
@app.callback(
	Output("flow-meter-readout-start-time", "children"),
	[Input("flow-meter-readout-start-button", "n_clicks")]
)
def flow_meter_start_readout(n_clicks):
	# print('start')
	# print(n_clicks)
	if n_clicks >= 1:
		return time.time()
	return 0.0

# Stop the flow meter readout from the database
@app.callback(
	Output("flow-meter-readout-stop-time", "children"),
	[Input("flow-meter-readout-stop-button", "n_clicks")]
)
def flow_meter_stop_readout(n_clicks):
	# print('stop')
	# print(n_clicks)
	if n_clicks >= 1:
		return time.time()
	return 1.0

# Button Control Panel
@app.callback(
	Output("flow-meter-readout-command-string", "children"),
	[Input("flow-meter-readout-start-time", "children"),
	Input("flow-meter-readout-stop-time", "children")]
)
def command_string(start, stop):
	master_command = {
		"START": start,
		"STOP": stop,
	}
	# print(master_command)
	recent_command = max(master_command, key=master_command.get)
	return recent_command


# Setpoint mass flow, store in hold
@app.callback(
	Output("flow-meter-setpoint-value", "children"),
	[Input("flow-meter-setpoint-numeric-input", "value")]
)
def flow_meter_setpoint_to_hold(setpoint_value):
	print(setpoint_value)
	# conver from mV to V
	setpoint_value = setpoint_value / 1000.0
	return setpoint_value

# Send hold setpoint mass flow to RPi
@app.callback(
	Output("flow-meter-setpoint-slider", "value"),
	[Input("flow-meter-setpoint-button", "n_clicks")],
	[State("flow-meter-setpoint-value", "children")]
)
def flow_meter_setpoint_button(n_clicks, setpoint_value):
	if n_clicks:
		print(f'Inside flow_meter_setpoint_button, n_clicks is {n_clicks}, setpoint_value is {setpoint_value}')
		#sanity check that it is between 0 and 5
		if (setpoint_value >= 0.0) & (setpoint_value < 5.0):

			# update field in the database
			setFlowMeterControlValues(setpoint_value, sql_engine)

			# set the value of the slider flow-meter-setpoint-slider"
			setpoint_value = round(setpoint_value * 1000)

			return setpoint_value
	else:
		return 0


# callback to read the database and store in a json objective
@app.callback(
	Output('flow-meter-readout-values', 'children'),
	[Input('readout-interval', 'n_intervals')],
	[State("flow-meter-readout-command-string", "children")]
	)
def retrieve_data(intervals, command_string):
	# print(state_dic)
	if command_string == 'START':

		df = readFlowMeterVoltage(sql_engine, 300)  # retrieve the past 60 seconds
		state_dic['state'] = 'plotting'

		return df.to_json(date_format='iso', orient='split')
	else:
		 state_dic['state'] = 'not plotting'

# Textarea Communication
@app.callback(
	Output("flow-meter-status-monitor", "value"),
	[Input("readout-interval", "n_intervals")],
	[State("flow-meter-setpoint-value", "children"),
	State("flow-meter-readout-command-string", "children"),
	State("flow-meter-readout-values", "children")]
)
def flow_meter_text_area(intervals,
	flow_meter_setpoint_value,
	command_string,
	json_data
	):
	if state_dic['state'] == "plotting":
		# print("plotting")
		df = pd.read_json(json_data, orient='split')
		last_db_reading = df.loc[0,'time']
		last_db_reading = pd.to_datetime(last_db_reading)
		last_db_reading = last_db_reading.strftime("%Y-%m-%d, %H:%M:%S")
	else:
		last_db_reading = -1


	status = (
		"-----------STATUS------------\n"
		+ "Readout status: " + str(command_string) + "\n"
		+ "Last reading mass flow received: " + str(last_db_reading) + "\n"
		+ "flow_meter_setpoint_value: " + str(flow_meter_setpoint_value) + " V"
	)

	return status


# Flow meter Graph
@app.callback(
	Output("flow-meter-readout-graph", "figure"),
	[Input("flow-meter-readout-values", "children")]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def plot_graph_data(json_data):

	# print(state_dic)
	traces = []

	try:
		df = pd.read_json(json_data, orient='split')
		# print('inside plot_graph_data, read df')
		# print(df.iloc[0,:])
		traces.append(go.Scatter(
			x=df['time'],
			y=df['read_voltage'],
			line=go.scatter.Line(
				color='#42C4F7',
				# width=2.0
			),
			text='Voltage [V]',
			# mode='markers',
			mode='lines+markers',
			opacity=1,

			name='Voltage [V]'
		))
		# set voltage
		traces.append(go.Scatter(
			x=df['time'],
			y=df['set_voltage'],
			text='Set voltage [V]',
			line=go.scatter.Line(
				color='orange',
				# width=1.5
			),
			# mode='markers',
			mode='lines+markers',
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			name='Set voltage [V]'
		))

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='dose [muSv/hr]',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='dose [muSv/hr]'
		))

	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'title': 'Time'},
			yaxis={'title': 'Voltage [V]', 'range': [0, 4]},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}
