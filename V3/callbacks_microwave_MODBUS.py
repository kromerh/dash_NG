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


host = "twofast-RPi3-0"  # your host
user = user  # username
passwd = pw  # password
db = "NG_twofast_DB" # name of the database
connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
try:
	sql_engine = sql.create_engine(connect_string)
except:
	print("Could not connect to DB")


def retrieve_power_data(sql_engine, pastEntries=2000):  # read past 1000 entries by default
    query = """SELECT * FROM microwave_generator_power ORDER BY id DESC LIMIT {}""".format(pastEntries)
    data = pd.read_sql(query, sql_engine)
    data = data[['time', 'FP', 'RP', 'power_setpoint']]
    # print(df_dose.head())
    return data

def retrieve_frequency_data(sql_engine, pastEntries=2000):  # read past 1000 entries by default
    query = """SELECT * FROM microwave_generator_frequency ORDER BY id DESC LIMIT {}""".format(pastEntries)
    data = pd.read_sql(query, sql_engine)
    data = data[['time', 'frequency', 'frequency_setpoint']]
    data['frequency'] = data['frequency'] / 10.0 # convert to MHz
    data['frequency_setpoint'] = data['frequency_setpoint'] / 10.0 # convert to MHz
    # print(df_dose.head())
    return data

def retrieve_state_data(sql_engine, pastEntries=2000):  # read past 1000 entries by default
    query = """SELECT * FROM microwave_generator_state ORDER BY id DESC LIMIT {}""".format(pastEntries)
    data = pd.read_sql(query, sql_engine)
    data = data[['time', 'status']]
    # print(df_dose.head())
    return data


# CALLBACKS

# callback to read the database and store in a json objective
@app.callback(
	Output('mw-db-power-values', 'children'),
	[Input('live-db-readout-interval', 'n_intervals')])
def cb_retrieve_power_data(n):
	pastEntries = 2000
	data = retrieve_power_data(sql_engine, pastEntries)
	return data.to_json(date_format='iso', orient='split')



# callback to read the database and store in a json objective
@app.callback(
	Output('mw-db-frequency-values', 'children'),
	[Input('live-db-readout-interval', 'n_intervals')])
def cb_retrieve_frequency_data(n):
	pastEntries = 2000
	data = retrieve_frequency_data(sql_engine, pastEntries)
	return data.to_json(date_format='iso', orient='split')


# callback to read the database and store in a json objective
@app.callback(
	Output('mw-db-status-values', 'children'),
	[Input('live-db-readout-interval', 'n_intervals')])
def cb_retrieve_state_data(n):
	pastEntries = 10
	data = retrieve_state_data(sql_engine, pastEntries)
	return data.to_json(date_format='iso', orient='split')



# power graph
@app.callback(
	Output('MW-Power-graph', 'figure'),
	[Input('mw-db-power-values', 'children')])
def cb_plot_power(json_data):
	traces = []
	try:
		data = pd.read_json(json_data, orient='split')

		# set a common x axis label!
		traces.append(go.Scatter(
			x=data['time'],
			y=data['FP'],
			line=go.scatter.Line(
				color='red',
				width=1.0
			),
			text='FP [W]',
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			mode='lines',
			name='FP [W]'
		))
		traces.append(go.Scatter(
			x=data['time'],
			y=data['RP'],
			line=go.scatter.Line(
				color='orange',
				width=1.0
			),
			text='RP [W]',
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			mode='lines',
			name='RP [W]'
		))
		traces.append(go.Scatter(
			x=data['time'],
			y=data['power_setpoint'],
			line=go.scatter.Line(
				color='blue',
				width=1.0
			),
			text='RP_set [W]',
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			mode='lines',
			name='RP_set [W]'
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
			yaxis={'title': 'Power [W]', 'range': [0, 201]},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}

# frequency graph
@app.callback(
	Output('MW-Frequency-graph', 'figure'),
	[Input('mw-db-frequency-values', 'children')])
def cb_plot_frequency(json_data):
	traces = []
	try:
		data = pd.read_json(json_data, orient='split')
    	# data = data[['time', 'frequency', 'frequency_setpoint']]

		# set a common x axis label!
		traces.append(go.Scatter(
			x=data['time'],
			y=data['frequency'],
			line=go.scatter.Line(
				color='red',
				width=1.0
			),
			text='F_read [MHz]',
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			mode='lines',
			name='F_read [MHz]'
		))
		traces.append(go.Scatter(
			x=data['time'],
			y=data['frequency_setpoint'],
			line=go.scatter.Line(
				color='orange',
				width=1.0
			),
			text='F_set [MHz]',
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			mode='lines',
			name='F_set [MHz]'
		))
		traces.append(go.Scatter(
			x=data['time'],
			y=data['power_setpoint'],
			line=go.scatter.Line(
				color='blue',
				width=1.0
			),
			text='RP_set [W]',
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			mode='lines',
			name='RP_set [W]'
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
			yaxis={'title': 'Frequency [MHz]', 'range': [2400, 2500]},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}


# Textarea Communication
@app.callback(
	Output("MW-status-monitor", "value"),
	[Input("mw-db-status-values", "n_intervals")]
)
def cb_mw_status_monitor(json_data):
	data = pd.read_json(json_data, orient='split')
	data = data.iloc[-1:,]
    # data = data[['time', 'status']]

	status = (
		"-----------STATUS------------\n"
		+ "Time: " + data['time'].values[0] + "\n"
		+ "Status: " + data['status'].values[0]
	)

	return status
