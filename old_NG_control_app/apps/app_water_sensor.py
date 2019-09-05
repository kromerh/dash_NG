import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime, time
import pymysql
import sqlalchemy as sql

from app import app
user = 'doseReader'
pw = 'heiko'

host="twofast-rpi3-0"  # your host
user=user # username
passwd=pw  # password
db="NG_twofast_DB" # name of the database
connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)

def get_water_sensor_data(sql_engine, pastSeconds=7200):  # read past 2hrs by default
    query = """SELECT * FROM water_sensor_data ORDER BY id DESC LIMIT {}""".format(pastSeconds)
    data = pd.read_sql(query, sql_engine)

    data = data[['time', 's1', 's2', 's3']]
    return data




hours_to_plot = 3 # plot the past 3 hours for the live stream

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
				html.H3('Water sensor data for the past {} hours'.format(hours_to_plot))
				], className='Title-center-header'),

			html.Div([
				html.H3(id='display-time-water')
				], className='Title-center'),

			html.Div([
			   dcc.Graph(id='indicator-graphic-live')
			   ], className='five columns live-plot'),  # displays HV data

		], className='row graph-row'),

		html.Hr(),

		# Hidden div inside the app that stores the data from the live db
		html.Div(
			[
				dcc.Interval(id="live-plot-update-water", interval=2000, n_intervals=0),
				html.Div(id='live-db-values-water')

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
@app.callback(
	Output('display-time-water', 'children'),
	[Input('live-plot-update-water', 'n_intervals')])
def display_time(n):
	return u'Last update: {}'.format(str(datetime.datetime.now()))

# callback to read the database and store in a json objective
@app.callback(
	Output('live-db-values-water', 'children'),
	[Input('live-plot-update-water', 'n_intervals')])
def retrieve_data(n):
	 t = int(float(hours_to_plot) * 3600.0)
	 data = get_water_sensor_data(sql_engine, t)  # retrieve the past 2 hrs

	 return data.to_json(date_format='iso', orient='split')

# callback to plot water sensor
@app.callback(
	Output('indicator-graphic-live', 'figure'),
	[Input('live-db-values', 'children')])
def update_graph(jsonified_cleaned_data):

	# more generally, this line would be
	# json.loads(jsonified_cleaned_data)
	df_live_db = pd.read_json(jsonified_cleaned_data, orient='split')
	# print(df_live_db.head())
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
	# sensor 1
	traces.append(go.Scatter(
		x=df_live_db['date'],
		y=df_live_db['s1'],
		text='sensor 1',
		line=go.scatter.Line(
			color='green',
			width=2
		),
		# mode='markers',
		opacity=0.7,
		# marker={
		#     'size': 15,
		#     'line': {'width': 0.5, 'color': 'white'}
		# },
		name='sensor 1'
	))
	# sensor2
	traces.append(go.Scatter(
		x=df_live_db['date'],
		y=df_live_db['s2'],
		text='sensor 2',
		line=go.scatter.Line(
			color='blue',
			width=2
		),
		# mode='markers',
		opacity=0.7,
		# marker={
		#     'size': 15,
		#     'line': {'width': 0.5, 'color': 'white'}
		# },
		name='sensor 2'
	))
	# sensor 3
	traces.append(go.Scatter(
		x=df_live_db['date'],
		y=df_live_db['s3'],
		text='sensor 3',
		line=go.scatter.Line(
			color='red',
			width=2
		),
		# mode='markers',
		opacity=0.7,
		# marker={
		#     'size': 15,
		#     'line': {'width': 0.5, 'color': 'white'}
		# },
		name='sensor 3'
	))


	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'type': 'date', 'title': 'Time'},
			yaxis={'title': ' ', 'range': [-0.1, 1.1]},
			margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}
