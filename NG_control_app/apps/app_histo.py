import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime, time
import pymysql

from app import app


def getAvailableHistoricalDates():
	# returns available dates from the database
	db = pymysql.connect(host="twofast-RPi3-0",  # your host
						 user="doseReader",  # username
						 passwd="heiko",  # password
						 db="NG_twofast_DB")  # name of the database
	# Create a Cursor object to execute queries.
	cur = db.cursor()
	try:
		# DOSE
		# sql = "SELECT DATE(time) FROM data_dose" # 16.8s
		sql = "SELECT DISTINCT DATE(time) FROM data_dose" # 5.7 s
		cur.execute(sql)
		rows = cur.fetchall()
		df = pd.DataFrame( [[ij for ij in i] for i in rows] )
		df.rename(columns={0: 'date'}, inplace=True)

		lst_dates = df['date'].apply(lambda x: '{}'.format(x))
		lst_dates = lst_dates.values.tolist()
	except:
		cur.rollback()

	cur.close()

	return lst_dates



################################################################################################################################################
# HISTORICAL route: layout
################################################################################################################################################
# gets the available dates in the database (based on data_dose)
lst_dates = getAvailableHistoricalDates()
# print(lst_dates)
layout = html.Div([
	html.H1(children='Neutron Generator Data Display - historical plotter'),
	html.H4('Select date:'),
	html.Div(
		dcc.Dropdown(id='date_dropdown',
			options=[{'label': i, 'value': i} for i in lst_dates],
			value=lst_dates[-1])
		),
	html.Button(id='button-plot-historical', n_clicks=0, children='Submit'),

	html.Hr(),

	html.Div(id='display-date-plotted'),

	dcc.Graph(id='indicator-graphic-historical'),  # displays the data

	html.Div(id='page-historical-content'),
	html.Br(),
	dcc.Link('Go to live data plotter', href='/apps/app_live'),
	html.Br(),
	dcc.Link('Go back to home', href='/')
])


################################################################################################################################################
# HISTORICAL callbacks
################################################################################################################################################
def retrieveHistoricalData(date):  # read past 2hrs by default
	db = pymysql.connect(host="twofast-RPi3-0",  # your host
						 user="doseReader",  # username
						 passwd="heiko",  # password
						 db="NG_twofast_DB")  # name of the database
	# Create a Cursor object to execute queries.
	cur = db.cursor()

	timeStart = '{} 00:00:00'.format(date)
	timeEnd = '{} 23:59:00'.format(date)
	try:
		# DOSE
		sql = "SELECT * FROM data_dose WHERE data_dose.time BETWEEN \"{}\" AND \"{}\" ".format(timeStart, timeEnd)
		cur.execute(sql)
		rows = cur.fetchall()
		df_dose = pd.DataFrame( [[ij for ij in i] for i in rows] )
		df_dose.rename(columns={0: 'ID', 1: 'time', 2: 'dose', 3: 'dose_voltage', 4: 'dose_corrected'}, inplace=True)
		# df_dose = df_dose.set_index(['time'])

		# HV POWER SUPPLY
		sql = "SELECT * FROM data_HV WHERE data_HV.time BETWEEN \"{}\" AND \"{}\" ".format(timeStart, timeEnd)
		cur.execute(sql)
		rows = cur.fetchall()
		df_HV = pd.DataFrame( [[ij for ij in i] for i in rows] )
		df_HV.rename(columns={0: 'ID', 1: 'time', 2: 'HV_voltage', 3: 'HV_current'}, inplace=True)
		# df_HV = df_HV.set_index(['time'])

		# PRESSURE
		df_pressure = pd.DataFrame()

	except:
		cur.rollback()

	cur.close()

	return df_dose, df_HV, df_pressure  # df_dose contains the neutron output!

# callback to display what date is plotted
@app.callback(
	dash.dependencies.Output('display-date-plotted', 'children'),
	[dash.dependencies.Input('button-plot-historical', 'n_clicks')],
	[dash.dependencies.State('date_dropdown', 'value')])
def set_date_to_be_plotted(n_clicks, date):
	return u'Plot for date: {}'.format(date)

# callback to retrieve the data and plot it
@app.callback(
	dash.dependencies.Output('indicator-graphic-historical', 'figure'),
	[dash.dependencies.Input('button-plot-historical', 'n_clicks')],
	[dash.dependencies.State('date_dropdown', 'value')])
def update_figure_historical(n_clicks, date):
	df_dose, df_HV, df_pressure = retrieveHistoricalData(date)  # retrieve the past 2 hrs
	# plot each
	# set a common x axis label!
	traces = []
	# DOSE
	traces.append(go.Scatter(
		x=df_dose['time'],
		y=df_dose['dose_corrected']/10,
		text='dose [0.1 muSv/hr]',
		# mode='markers',
		opacity=0.7,
		# marker={
		#     'size': 15,
		#     'line': {'width': 0.5, 'color': 'white'}
		# },
		name='dose [0.1 muSv/hr]'
	))
	# HV voltage
	traces.append(go.Scatter(
		x=df_HV['time'],
		y=df_HV['HV_voltage'],
		text='HV_voltage [-kV]',
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
		x=df_HV['time'],
		y=df_HV['HV_current']*100,
		text='HV_current [-100 mA]',
		# mode='markers',
		opacity=0.7,
		# marker={
		#     'size': 15,
		#     'line': {'width': 0.5, 'color': 'white'}
		# },
		name='HV_current [-100 mA]'
	))

	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'type': 'date', 'title': 'Time'},
			yaxis={'title': 'Y', 'range': [0, 150]},
			margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}
