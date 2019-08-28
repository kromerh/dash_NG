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


# Microwave Mallah control
threshold_temperature_max = 28 # threshold below which the temperature should be
threshold_temperature_min = 19 # threshold above which the temperature should be

setpoint_power_max =  500.0  # maximal power of the microwave
setpoint_frequency_max =  2500  # maximal frequency of the microwave

################################################################################################################################################
# function
################################################################################################################################################

# ********************
# MICROWAVE GENERATOR
# ********************

def getFrequency(sql_engine):
	"""
	Reads the last 300 entries of the frequency and returns it in a dataframe
	"""
	query = "SELECT * FROM microwave_generator_frequency ORDER BY id DESC LIMIT 300"
	df = pd.read_sql(query, sql_engine)

	# columns: time (timestamp), frequency (float), id (primary key)
	return df

def getPower(sql_engine):
	"""
	Reads the last 300 entries of the power and returns it in a dataframe
	"""
	query = "SELECT * FROM microwave_generator_power ORDER BY id DESC LIMIT 300"
	df = pd.read_sql(query, sql_engine)

	# columns: time (timestamp), power (float), id (primary key)
	return df

def getReflectedPower(sql_engine):
	"""
	Reads the last 300 entries of the power and returns it in a dataframe
	"""
	query = "SELECT * FROM microwave_generator_reflected_power ORDER BY id DESC LIMIT 300"
	df = pd.read_sql(query, sql_engine)

	# columns: time (timestamp), power (float), id (primary key)
	return df

def getDLL(sql_engine):
	"""
	Reads the last 300 entries of the power and returns it in a dataframe
	"""
	query = "SELECT * FROM microwave_generator_DLL ORDER BY id DESC LIMIT 300"
	df = pd.read_sql(query, sql_engine)

	# columns: time (timestamp), power (float), id (primary key)
	return df

def getTemperature(sql_engine):
	"""
	Reads the last 300 entries of the two temperatures and returns it in a dataframe
	"""
	query = "SELECT * FROM microwave_generator_temperature ORDER BY id DESC LIMIT 300"
	df = pd.read_sql(query, sql_engine)

	# columns: time (timestamp), temperature1 (float), temperature2 (float), id (primary key)
	return df

def getState(sql_engine):
	"""
	Reads the last 10 entries of the two temperatures and returns it in a dataframe
	"""
	query = "SELECT * FROM microwave_generator_state ORDER BY id DESC LIMIT 10"
	df = pd.read_sql(query, sql_engine)

	# columns: time (timestamp), relais_5 (tinyint), relais_24 (tinyint), rf_status (tinyint), id (primary key)
	return df

def returnRedOrGreen(value_state):
	if len(value_state.index) > 1: # more than one value
		# find the position of 1
		vals_0 = value_state[value_state.index == 0].values[0]
		vals_1 = value_state[value_state.index == 1].values[0]
		if vals_1 > vals_0:
			return "green"
		else:
			return "red"
	else:  # only one value
		if value_state.index.values[0] == 1: # 1
			return "green"
		else: # 0
			return "red"


# ********************************
# MICROWAVE
# ********************************



# Send to the database



# Setpoint POWER

@app.callback(
	Output("microwave-power-setpoint", "children"),
	[Input("microwave-power-send-button", "n_clicks"),
	Input("microwave-power-slider", "value")]
)
def microwave_power_setpoint_button(n_clicks, setpoint_value):
	if n_clicks:
		print(f'Inside microwave_power_setpoint_button, n_clicks is {n_clicks}, setpoint_value is {setpoint_value}')
		#sanity check that it is between 0 and setpoint_power_max
		if (setpoint_value > 0.0) & (setpoint_value <= setpoint_power_max):

			# add command into the database
			setpoint_value = np.around(setpoint_value, decimals=1) # round to 0.1 values
			cmd = f'$PWR,{setpoint_value}'
			sendCommandToDatabase(cmd, sql_engine)

			return setpoint_value
	else:

		return 0  # return 0 as the setpoint by default


# Setpoint Frequency

@app.callback(
	Output("microwave-frequency-setpoint", "children"),
	[Input("microwave-frequency-send-button", "n_clicks"),
	Input("microwave-frequency-slider", "value")]
)
def microwave_frequency_setpoint_button(n_clicks, setpoint_value):
	if n_clicks:
		print(f'Inside microwave_frequency_setpoint_button, n_clicks is {n_clicks}, setpoint_value is {setpoint_value}')
		#sanity check that it is between 0 and setpoint_frequency_max
		if (setpoint_value > 0.0) & (setpoint_value <= setpoint_frequency_max):

			# add command into the database
			setpoint_value = np.around(setpoint_value, decimals=0).astype(int) # round to 1.0 values and store as integer
			cmd = f'$FRQ,{setpoint_value}'
			sendCommandToDatabase(cmd, sql_engine)

			return setpoint_value
	else:

		return 0  # return 0 as the setpoint by default


# Turn RF on

@app.callback(
	Output("microwave-rf-onOff", "children"),
	[Input("microwave-RF-start", "n_clicks")] # TODO: Check what goes here
)
def microwave_frequency_setpoint_button(n_clicks, setpoint_value):
	if n_clicks:
		print(f'Inside microwave_frequency_setpoint_button, n_clicks is {n_clicks}, setpoint_value is {setpoint_value}')
		#sanity check that it is between 0 and setpoint_frequency_max
		if (setpoint_value > 0.0) & (setpoint_value <= setpoint_frequency_max):

			# add command into the database
			setpoint_value = np.around(setpoint_value, decimals=0).astype(int) # round to 1.0 values and store as integer
			cmd = f'$FRQ,{setpoint_value}'
			sendCommandToDatabase(cmd, sql_engine)

			return setpoint_value
	else:

		return 0  # return 0 as the setpoint by default



# READ FROM THE DATABASE


# STATE

# Read the states from the database
@app.callback(
	Output("microwave-state-values", "children"),
	[Input("microwave-readout-interval", "n_intervals")]
)
def microwave_read_state(n_intervals):
	# call the function to read the state df
	df = getState(sql_engine)

	return df.to_json(date_format='iso', orient='split')

# temperature

# Read the states from the database
@app.callback(
	Output("microwave-temperature-values", "children"),
	[Input("microwave-readout-interval", "n_intervals")]
)
def microwave_read_remperature(n_intervals):
	# call the function to read the state df
	df = getTemperature(sql_engine)

	return df.to_json(date_format='iso', orient='split')

# power

# Read the power from the database
@app.callback(
	Output("microwave-power-values", "children"),
	[Input("microwave-readout-interval", "n_intervals")]
)
def microwave_read_power(n_intervals):
	# call the function to read the state df
	df = getPower(sql_engine)

	return df.to_json(date_format='iso', orient='split')

# frequency

# Read the frequency from the database
@app.callback(
	Output("microwave-frequency-values", "children"),
	[Input("microwave-readout-interval", "n_intervals")]
)
def microwave_read_frequency(n_intervals):
	# call the function to read the state df
	df = getFrequency(sql_engine)

	return df.to_json(date_format='iso', orient='split')


# Reflected power

# Read the reflected power from the database
@app.callback(
	Output("microwave-reflected-power-values", "children"),
	[Input("microwave-readout-interval", "n_intervals")]
)
def microwave_read_reflected_power(n_intervals):
	# call the function to read the state df
	df = getReflectedPower(sql_engine)

	return df.to_json(date_format='iso', orient='split')


# DLL
# Read the DLL from the database
@app.callback(
	Output("microwave-DLL-values", "children"),
	[Input("microwave-readout-interval", "n_intervals")]
)
def microwave_read_DLL(n_intervals):
	# call the function to read the state df
	df = getDLL(sql_engine)

	return df.to_json(date_format='iso', orient='split')



# STATUS CONTROL: Coloring the LEDs


# Color 24V relais red or green depending on its state
@app.callback(
	Output("microwave-24V-indicator", "color"),
	[Input("microwave-state-values", "children")]
)
def microwave_color_relais_24(json_data):
	# check if the last entries in the relais 24 column are majority 1, then return 1 for green otherwise 0 for red
	df = pd.read_json(json_data, orient='split')
	vals = df['relais_24'].value_counts()

	return returnRedOrGreen(vals)

# Color 5V relais red or green depending on its state
@app.callback(
	Output("microwave-5V-indicator", "color"),
	[Input("microwave-state-values", "children")]
)
def microwave_color_relais_5(json_data):
	df = pd.read_json(json_data, orient='split')
	# check if the last entries in the relais 5 column are majority 1, then return 1 for green otherwise 0 for red
	vals = df['relais_5'].value_counts()

	return returnRedOrGreen(vals)

# Color rf relais red or green depending on its state
@app.callback(
	Output("microwave-RF-indicator", "color"),
	[Input("microwave-state-values", "children")]
)
def microwave_color_relais_rf(json_data):
	df = pd.read_json(json_data, orient='split')
	# check if the last entries in the rf_status column are majority 1, then return 1 for green otherwise 0 for red
	vals = df['rf_status'].value_counts()

	return returnRedOrGreen(vals)


# Color temperature indicator red or green depending on its state
@app.callback(
	Output("microwave-temp-indicator", "color"),
	[Input("microwave-temperature-values", "children")]
)
def microwave_color_temperature_indicator(json_data):
	df = pd.read_json(json_data, orient='split')

	t1 = df['temperature1'].median()
	t2 = df['temperature2'].median()

	if ((t1 < threshold_temperature_max) and (t1 > threshold_temperature_min)) and ((t2 < threshold_temperature_max) and (t2 > threshold_temperature_min)):
		return "green"
	else:
		return "red"


# POWER, FREQUENCY, TEMPERATURE indicators

# Display power
@app.callback(
	Output("microwave-power-display", "value"),
	[Input("microwave-power-values", "children")]
)
def microwave_display_power(json_data):
	df = pd.read_json(json_data, orient='split')
	# take the mean of the last 10 entries
	vals = df['power'].values[0:11]

	return np.rint(np.mean(vals))

# Display frequency
@app.callback(
	Output("microwave-frequency-display", "value"),
	[Input("microwave-frequency-values", "children")]
)
def microwave_display_frequency(json_data):
	df = pd.read_json(json_data, orient='split')
	# take the mean of the last 10 entries
	vals = df['frequency'].values[0:11]

	return np.rint(np.mean(vals))

# Display temperature1
@app.callback(
	Output("microwave-temperature1-display", "value"),
	[Input("microwave-temperature-values", "children")]
)
def microwave_display_temperature1(json_data):
	df = pd.read_json(json_data, orient='split')
	# take the mean of the last 10 entries
	vals = df['temperature1'].values[0:11]

	return np.rint(np.mean(vals))

# Display temperature2
@app.callback(
	Output("microwave-temperature2-display", "value"),
	[Input("microwave-temperature-values", "children")]
)
def microwave_display_temperature2(json_data):
	df = pd.read_json(json_data, orient='split')
	# take the mean of the last 10 entries
	vals = df['temperature2'].values[0:11]

	return np.rint(np.mean(vals))



# GRAPHS


# Power Graph
@app.callback(
	Output("microwave-power-graph", "figure"),
	[Input("microwave-power-values", "children")]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def plot_power_graph_data(json_data):

	traces = []

	try:
		df = pd.read_json(json_data, orient='split')

		# print(df.iloc[0,:])
		traces.append(go.Scatter(
			x=df['time'],
			y=df['power'],
			line=go.scatter.Line(
				color='#42C4F7',
				# width=2.0
			),
			text='Power [W]',
			# mode='markers',
			mode='lines+markers',
			opacity=1,

			name='Power [W]'
		))

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='Power [W]',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='Power [W]'
		))

	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'title': 'Time'},
			yaxis={'title': 'Power [W]'},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}


# Frequency Graph
@app.callback(
	Output("microwave-frequency-graph", "figure"),
	[Input("microwave-frequency-values", "children")]
)
def plot_frequency_graph_data(json_data):

	traces = []

	try:
		df = pd.read_json(json_data, orient='split')

		# print(df.iloc[0,:])
		traces.append(go.Scatter(
			x=df['time'],
			y=df['frequency'],
			line=go.scatter.Line(
				color='#42C4F7',
				# width=2.0
			),
			text='Frequency [MHz]',
			# mode='markers',
			mode='lines+markers',
			opacity=1,

			name='Frequency [MHz]'
		))

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='Frequency [MHz]',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='Frequency [MHz]'
		))

	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'title': 'Time'},
			yaxis={'title': 'Frequency [MHz]'},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}


# Temperature Graph
@app.callback(
	Output("microwave-temperature-graph", "figure"),
	[Input("microwave-temperature-values", "children")]
)
def plot_tempperature_graph_data(json_data):

	traces = []

	try:
		df = pd.read_json(json_data, orient='split')

		traces.append(
			go.Scatter(
				x=df['time'],
				y=df['temperature1'],
				line=go.scatter.Line(
					color='#42C4F7',
					# width=2.0
				),
				text='Temperature 1 [degC]',
				# mode='markers',
				mode='lines+markers',
				opacity=1,

				name='Temperature 1 [degC]'
			)
		)
		traces.append(
			go.Scatter(
				x=df['time'],
				y=df['temperature2'],
				line=go.scatter.Line(
					color='#e542f7',
					# width=2.0
				),
				text='Temperature 2 [degC]',
				# mode='markers',
				mode='lines+markers',
				opacity=1,

				name='Temperature 2 [degC]'
			)
		)

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='Frequency [MHz]',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='Frequency [MHz]'
		))

	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'title': 'Time'},
			yaxis={'title': 'Temperature [degC]'},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}


# Reflected Power Graph
@app.callback(
	Output("microwave-reflected-power-graph", "figure"),
	[Input("microwave-reflected-power-values", "children")]
)
def plot_reflected_power_graph_data(json_data):

	traces = []

	try:
		df = pd.read_json(json_data, orient='split')

		traces.append(
			go.Scatter(
				x=df['time'],
				y=df['power_out'],
				line=go.scatter.Line(
					color='#42C4F7',
					# width=2.0
				),
				text='Power out [W]',
				# mode='markers',
				mode='lines+markers',
				opacity=1,

				name='Power out [W]'
			)
		)
		traces.append(
			go.Scatter(
				x=df['time'],
				y=df['power_reflected'],
				line=go.scatter.Line(
					color='#e542f7',
					# width=2.0
				),
				text='Power reflected [W]',
				# mode='markers',
				mode='lines+markers',
				opacity=1,

				name='Power reflected [W]'
			)
		)

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='Power [W]',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='Frequency [MHz]'
		))

	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'title': 'Time'},
			yaxis={'title': 'Power [W]'},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}

# DLL Graph
@app.callback(
	Output("microwave-DLL-graph", "figure"),
	[Input("microwave-DLL-values", "children")]
)
def plot_DLL_graph_data(json_data):

	traces = []

	try:
		df = pd.read_json(json_data, orient='split')

		traces.append(
			go.Scatter(
				x=df['time'],
				y=df['DLL_frequency'],
				line=go.scatter.Line(
					color='#42C4F7',
					# width=2.0
				),
				text='DLL frequency [MHz]',
				# mode='markers',
				mode='lines+markers',
				opacity=1,

				name='DLL frequency [MHz]'
			)
		)
		traces.append(
			go.Scatter(
				x=df['time'],
				y=df['DLL_reflexion'],
				line=go.scatter.Line(
					color='#e542f7',
					# width=2.0
				),
				yaxis='y2',
				text='DLL reflexion [dB]',
				# mode='markers',
				mode='lines+markers',
				opacity=1,

				name='DLL reflexion [dB]'
			)
		)

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='Power [W]',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='Frequency [MHz]'
		))

	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'title': 'Time'},
			yaxis={'title': 'Frequency'},
			yaxis2 = dict(title= 'Reflexion [dB]', overlaying='y', side='right'),
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}