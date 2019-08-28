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

def retrieveLiveData(sql_engine, pastSeconds=7200):  # read past 2hrs by default
    query = """SELECT * FROM HBox_Uno ORDER BY id DESC LIMIT {}""".format(pastSeconds)
    df_dose = pd.read_sql(query, sql_engine)
    df_dose['dose'] = df_dose['dose_voltage'] * 3000 / 5.5  # conversion factors according to current output signal muSv/hr
    df_dose['date'] = df_dose['time']

    df_dose = df_dose[['date', 'dose', 'HV_current', 'HV_voltage']]
    # print(df_dose.head())
    return df_dose




# callback to read the database and store in a json objective
@app.callback(
	Output('live-db-values', 'children'),
	[Input('live-db-readout-interval', 'n_intervals')])
def retrieve_data(n):
	 t = int(float(0.5) * 3600.0)
	 # some expensive clean data step
	 df_live_db = retrieveLiveData(sql_engine, t)  # retrieve the past 2 hrs
	 # print(df_live_db.head())
	 # more generally, this line would be
	 # json.dumps(cleaned_df)
	 return df_live_db.to_json(date_format='iso', orient='split')


# dose graph
@app.callback(
	Output('Dose-graph', 'figure'),
	[Input('live-db-values', 'children')])
def cb_plot_dose(json_data):
	traces = []
	try:
		df_live_db = pd.read_json(json_data, orient='split')
		# print(df_live_db.head())
		# plot each
		# set a common x axis label!
		traces.append(go.Scatter(
			x=df_live_db['date'],
			y=df_live_db['dose'],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='dose [muSv/hr]',
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			mode='lines',
			name='dose [muSv/hr]'
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
			yaxis={'title': 'Dose [muShv/hr]', 'range': [0, 1000]},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}


# HV graph
@app.callback(
	Output("HV-graph", "figure"),
	[Input("live-db-values", "children")]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def cb_plot_hv_graph(json_data):

	# print(state_dic)
	traces = []

	try:
		df_live_db = pd.read_json(json_data, orient='split')
		# print(df_live_db.head())
		traces.append(go.Scatter(
			x=df_live_db['date'],
			y=df_live_db['HV_voltage'],
			text='HV_voltage [x -1kV]',
			line=go.scatter.Line(
				color='red',
				width=1.5
			),
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			name='HV_voltage [-kV]'
		))
		# HV current
		traces.append(go.Scatter(
			x=df_live_db['date'],
			y=df_live_db['HV_current']*100,
			text='HV_current [x -100mA]',
			line=go.scatter.Line(
				color='orange',
				width=1.5
			),
			# mode='markers',
			opacity=0.7,
			# marker={
			#     'size': 15,
			#     'line': {'width': 0.5, 'color': 'white'}
			# },
			name='HV_current [-100 mA]'
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
			yaxis={'title': 'HV [-]', 'range': [0, 150]},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}
