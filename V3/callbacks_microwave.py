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


SP_P_max =  200.0  # Setpoint maximal power
SP_F_min = 2400.0 # Setpoint minimum frequency
SP_F_max = 2500.0 # Setpoint maximum frequency (steps of 100 kHz)
d_F = 0.1 #

# DATABASE

def read_power_table(sql_engine, pastSeconds=60): # read past 60secs by default
	"""
	Read the power table from the database
	"""
	query = "SELECT * FROM microwave_generator_power ORDER BY id DESC LIMIT %(pastSeconds)s" % {"pastSeconds": pastSeconds}
	df = pd.read_sql(query, sql_engine)
	# print(df)
	return df

def read_frequency_table(sql_engine, pastSeconds=60): # read past 60secs by default
	"""
	Read the power table from the database
	"""
	query = "SELECT * FROM microwave_generator_frequency ORDER BY id DESC LIMIT %(pastSeconds)s" % {"pastSeconds": pastSeconds}
	df = pd.read_sql(query, sql_engine)

	return df

def read_state_table(sql_engine, pastSeconds=60): # read past 60secs by default
	"""
	Read the power table from the database
	"""
	query = "SELECT * FROM microwave_generator_state ORDER BY id DESC LIMIT %(pastSeconds)s" % {"pastSeconds": pastSeconds}
	df = pd.read_sql(query, sql_engine)

	return df





# CALLBACKS

# Textarea Communication
@app.callback(
	Output("microwave-status-monitor", "value"),
	[Input("microwave-readout-interval", "n_intervals")],
	[State("microwave-power-values", "children")]
)
def microwave_text_area(intervals,
	json_data
	):
	last_db_reading = -1
	try:
		df = pd.read_json(json_data, orient='split')
		if len(df) > 0:
			last_db_reading = df.loc[0,'time']
			last_db_reading = pd.to_datetime(last_db_reading)
			last_db_reading = last_db_reading.strftime("%Y-%m-%d, %H:%M:%S")
		else:
			last_db_reading = -1
	except:
		pass


	status = (
		"-----------STATUS------------\n"
		+ "Last reading microwave power (FP) received: " + str(last_db_reading) + "\n"
	)

	return status


# microwave-power-values
# callback to read the database and store in a json objective
@app.callback(
	Output('microwave-power-values', 'children'),
	[Input('microwave-readout-interval', 'n_intervals')]
	)
def cb_read_power_table(intervals):
	df = read_power_table(sql_engine, 120)  # retrieve the past 60 seconds
	return df.to_json(date_format='iso', orient='split')


# microwave-frequency-values
# callback to read the database and store in a json objective
@app.callback(
	Output('microwave-frequency-values', 'children'),
	[Input('microwave-readout-interval', 'n_intervals')]
	)
def cb_read_frequency_table(intervals):
	df = read_frequency_table(sql_engine, 120)  # retrieve the past 60 seconds
	return df.to_json(date_format='iso', orient='split')

# microwave-MW-state-values
# callback to read the database and store in a json objective
@app.callback(
	Output('microwave-MW-state-values', 'children'),
	[Input('microwave-readout-interval', 'n_intervals')]
	)
def cb_read_state_table(intervals):
	df = read_state_table(sql_engine, 120)  # retrieve the past 60 seconds
	return df.to_json(date_format='iso', orient='split')






# microwave power graph
@app.callback(
	Output("microwave-power-graph", "figure"),
	[Input("microwave-power-values", "children")]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def cb_plot_power_graph(json_data):

	# print(state_dic)
	traces = []

	try:
		data = pd.read_json(json_data, orient='split')
		# print(data.head())
		traces.append(
			go.Scatter(
				x=data['time'],
				y=data['FP'],
				line=go.scatter.Line(
					color='#42C4F7',
					# width=2.0
				),
				text='Forward power [W]',
				# mode='markers',
				mode='lines',
				opacity=1,

				name='FP [W]'
			)
		)
		traces.append(
			go.Scatter(
				x=data['time'],
				y=data['RP'],
				line=go.scatter.Line(
					color='red',
					# width=2.0
				),
				text='Reflected power [W]',
				# mode='markers',
				mode='lines',
				opacity=1,

				name='RP [W]'
			)
		)
		traces.append(
			go.Scatter(
				x=data['time'],
				y=data['power_setpoint'],
				line=go.scatter.Line(
					color='green',
					# width=2.0
				),
				text='Setpoint power [W]',
				# mode='markers',
				mode='lines',
				opacity=1,

				name='SP [W]'
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
			yaxis={'title': 'Power [W]', 'range':[0,205]},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}



# microwave frequency graph
@app.callback(
	Output("microwave-frequency-graph", "figure"),
	[Input("microwave-frequency-values", "children")]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def cb_plot_frequency_graph(json_data):

	# print(state_dic)
	traces = []

	try:
		data = pd.read_json(json_data, orient='split')
		# print(data.head())
		traces.append(
			go.Scatter(
				x=data['time'],
				y=data['frequency'],
				line=go.scatter.Line(
					color='#42C4F7',
					# width=2.0
				),
				text='Frequency [MHz]',
				# mode='markers',
				mode='lines',
				opacity=1,

				name='FP [W]'
			)
		)
		traces.append(
			go.Scatter(
				x=data['time'],
				y=data['frequency_setpoint'],
				line=go.scatter.Line(
					color='green',
					# width=2.0
				),
				text='Setpoint frequency [MHz]',
				# mode='markers',
				mode='lines',
				opacity=1,

				name='SP [W]'
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
			yaxis={'title': 'Frequency [MHz]', 'range':[2300,2600]},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}

