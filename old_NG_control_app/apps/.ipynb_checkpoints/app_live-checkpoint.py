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


hours_to_plot = 3 # plot the past 3 hours for the live stream
hours_to_plot_today = 12 # plot the past 12 hours for the today stream
################################################################################################################################################
# LIVE route: layout
################################################################################################################################################


layout = html.Div(children=[
		html.Div([
		   html.H1(children='Neutron Generator Data Display - live plotter')
		   ], className='banner'),

		html.Hr(),

		html.Div([
			html.Div([
				html.H3('Live stream for the past {} hours'.format(hours_to_plot))
				], className='Title-center-header'),

			html.Div([
				html.H3(id='display-time')
				], className='Title-center'),

			html.Div([
			   dcc.Graph(id='indicator-graphic-live-HV')
			   ], className='five columns live-plot'),  # displays HV data

			html.Div([
			   dcc.Graph(id='indicator-graphic-live-dose')
			   ], className='five columns live-plot'),  # displays Dose

		], className='row graph-row'),

		html.Hr(),

		html.Div([
			html.Div([
				html.H3('Past 12 hours of data')
				], className='Title-center-header'),
			html.Div([
				html.Button(id='button-plot-today', n_clicks=0, children='Update')
				], className='button-update-today-plot'),
			html.Div([
			   dcc.Graph(id='indicator-graphic-today')
			   ], className='ten columns live-plot'),  # displays HV data


		], className='row graph-row'),

		# Hidden div inside the app that stores the data from the live db
		html.Div(
			[
				dcc.Interval(id="live-plot-update", interval=5000, n_intervals=0),
				html.Div(id='live-db-values')

			],
			style={"visibility": "hidden"},
		),

		html.Div([
			html.Div(id='page-live-content'),
			html.Br(),
			dcc.Link('Go to historical data plotter', href='/apps/app_histo'),
			html.Br(),
			dcc.Link('Go back to home', href='/'),
		]),
	])


################################################################################################################################################
# LIVE callbacks
################################################################################################################################################
# callback to update the label that indicates when the last query was exec
# @app.callback(
# 	Output('display-time', 'children'),
# 	[Input('live-plot-update', 'n_intervals')])
# def display_time(n):
# 	return u'Last update: {}'.format(str(datetime.datetime.now()))

# callback to read the database and store in a json objective
@app.callback(
	Output('live-db-values', 'children'),
	[Input('live-plot-update', 'n_intervals')])
def retrieve_data(n):
	 t = int(float(hours_to_plot) * 3600.0)
	 # some expensive clean data step
	 df_live_db = retrieveLiveData(t)  # retrieve the past 2 hrs
	 print(df_live_db.head())
	 # more generally, this line would be
	 # json.dumps(cleaned_df)
	 return df_live_db.to_json(date_format='iso', orient='split')

# callback to plot data HV
@app.callback(
	Output('indicator-graphic-live-HV', 'figure'),
	[Input('live-db-values', 'children')])
def update_graph(jsonified_cleaned_data):

	# more generally, this line would be
	# json.loads(jsonified_cleaned_data)
	df_live_db = pd.read_json(jsonified_cleaned_data, orient='split')

	# plot each
	# set a common x axis label!
	traces = []
	# traces.append(go.Scatter(
	# 	x=df_live_db['date'],
	# 	y=df_live_db['dose']/10,
	# 	text='dose [0.1 muSv/hr]',
	# 	# mode='markers',
	# 	opacity=0.7,
	# 	# marker={
	# 	#     'size': 15,
	# 	#     'line': {'width': 0.5, 'color': 'white'}
	# 	# },
	# 	name='dose [0.1 muSv/hr]'
	# ))
	# HV voltage
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

	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'type': 'date', 'title': 'Time'},
			yaxis={'title': ' ', 'range': [0, 150]},
			margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}

# callback to plot data dose
@app.callback(
	Output('indicator-graphic-live-dose', 'figure'),
	[Input('live-db-values', 'children')])
def update_graph(jsonified_cleaned_data):

	# more generally, this line would be
	# json.loads(jsonified_cleaned_data)
	df_live_db = pd.read_json(jsonified_cleaned_data, orient='split')

	# plot each
	# set a common x axis label!
	traces = []
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


	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'type': 'date', 'title': 'Time'},
			yaxis={'title': 'Dose [muSv/hr]', 'range': [0, 1000]},
			margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}

################################################################################################################################################
# Today callbacks
################################################################################################################################################

# callback to retrieve the data and plot it
@app.callback(
	dash.dependencies.Output('indicator-graphic-today', 'figure'),
	[dash.dependencies.Input('button-plot-today', 'n_clicks')])
def update_figure_today(n_clicks):
	t = int(float(hours_to_plot_today) * 3600.0)
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
		x=df_dose['date'],
		y=df_dose['HV_current']*100,
		text='HV_current [-100 mA]',
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
