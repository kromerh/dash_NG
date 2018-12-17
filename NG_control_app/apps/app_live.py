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

def retrieveLiveData(pastSeconds=7200):  # read past 2hrs by default
	db = pymysql.connect(host="twofast-RPi3-0",  # your host
						 user="doseReader",  # username
						 passwd="heiko",  # password
						 db="NG_twofast_DB")  # name of the database
	# Create a Cursor object to execute queries.
	cur = db.cursor()

	try:
		# DOSE
		cur.execute("""SELECT * FROM HBox_Uno ORDER BY id DESC LIMIT {}""".format(pastSeconds))
		rows = cur.fetchall()
		# print('got dose')
		df_dose = pd.DataFrame( [[ij for ij in i] for i in rows] )
		# voltage_dose, counts_WS, counts_BS, counts_DF
		df_dose.rename(columns={0: 'ID', 1: 'date', 2: 'dose_voltage', 3: 'HV_current', 4: 'HV_voltage'}, inplace=True)
		df_dose = df_dose.set_index(['ID'])
		df_dose['dose'] = df_dose['dose_voltage'] * 3000 / 5.5  # conversion factors according to current output signal muSv/hr
		# df_dose['dose_corr'] = interp_dose(df_dose['dose'])  # uses the lookup table


	except:
		print('Error in retrieveLiveData')


	return df_dose

################################################################################################################################################
# LIVE route: layout
################################################################################################################################################

layout = html.Div(children=[
	html.H1(children='Neutron Generator Data Display - live plotter'),

    html.Label('Live stream for the past 2 hours:'),
    html.Hr(),
    html.Div(id='display-time'),
	dcc.Graph(id='indicator-graphic-live'),  # displays the data
	html.Div(id='page-live-content'),
	html.Br(),
	dcc.Link('Go to historical data plotter', href='/apps/app_histo'),
	html.Br(),
	dcc.Link('Go back to home', href='/'),

])



################################################################################################################################################
# LIVE callbacks
################################################################################################################################################
@app.callback(
    dash.dependencies.Output('display-time', 'children'),
    events=[dash.dependencies.Event('my-interval', 'interval')])
def display_time():
    return u'Last update: {}'.format(str(datetime.datetime.now()))


@app.callback(
    dash.dependencies.Output('my-interval', 'interval'),
    [dash.dependencies.Input('set-time', 'value')])
def update_interval(value):
    return value

# Display how many past seconds will be plotted
@app.callback(
	dash.dependencies.Output('display-selected-values', 'children'),
	[dash.dependencies.Input('hours_to_plot', 'value')])
def set_cities_options(hours_to_plot):
	return u'Plotting past {} seconds...'.format(float(hours_to_plot)*3600.0)

# callback to retrieve the data and plot it
@app.callback(
	dash.dependencies.Output('indicator-graphic-live', 'figure'),
	[dash.dependencies.Input('hours_to_plot', 'value')],
	events=[dash.dependencies.Event('my-interval', 'interval')]
	)
def update_figure(hours_to_plot):
	t = int(float(hours_to_plot) * 3600.0)
	df_dose = retrieveLiveData(t)  # retrieve the past 2 hrs
	# plot each
	# set a common x axis label!
	traces = []
	# DOSE
	# print(df_dose.head())
	traces.append(go.Scatter(
		x=df_dose['date'],
		y=df_dose['dose']/10,
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
		x=df_dose['date'],
		y=df_dose['HV_voltage'],
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
		x=df_dose['date'],
		y=df_dose['HV_current']*100,
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
