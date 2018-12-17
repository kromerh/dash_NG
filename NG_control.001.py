# TODO:

# * Plot pressure and output in subplots, shared x plot! https://plot.ly/python/subplots/#subplots-with-shared-xaxes
# * connect to db in file, no info in script!
# * enable plotting of neutron output
# * enable plotting of pressure
# * maybe: add export function


# DONE
# D Include dose lookup table in subfolder
# D Include MCNP files in subfolder

# -*- coding: utf-8 -*-
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import datetime, time
import pymysql
# from scipy.interpolate import interp1d
import plotly.graph_objs as go

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

# Dash CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

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



# FUNCTIONS FOR THE NEUTRON OUTPUT COMPUTATION
def compute_output(HV, dose):
	try:
		# neutronOutputPer100muSv = interp_output(HV)
		neutronOutputPer100muSv = interp_output(HV)
	except ValueError:
		# take 80 kV if the HV is not in the interpolation range
		neutronOutputPer100muSv = lst_output[0]

	return (dose/100) * neutronOutputPer100muSv
def getNeutronOutputPer100muSv(HV=100, LB6411_distance=70):
	"""
	Retrieves the neutron output per 100µSv/h as determined from MCNP. Only works for the new target. Returns that value
	HV: High voltage. This determines which MCNP run is taken to load the data. Default is -100 kV
	LB6411_distance: Distance between the source and LB6411 position. Default is 70 cm
	"""
	# list of the HV's simulated in MCNP
	lst_HV = [80,85,90,95,100,105,110]
	# list of the ID's for the respective MCNP simulation
	lst_ID = [230,231,232,233,234,235,236]
	# find index of the HV in the lst_HV
	try:
		idx = lst_HV.index(HV)
	except ValueError:
		idx = -1

	if idx == -1:
		print('--- High voltage value of ' + str(HV) + ' is not in an MCNP run. Exit SCRIPT. --- ')
		sys.exit()
	else:
		# TODO: change this into a common directory and select from the HV, maybe as an interpolation
		path_to_MCNP_OutputPer100muSv = './MCNP/CurrentTarget%s/CurrentTarget%s_normal/' % (lst_ID[idx], lst_ID[idx])
		csv_name = 'df_neutron_output_for_Edeut_%s.csv' % HV
		df = pd.read_csv(path_to_MCNP_OutputPer100muSv + csv_name, header=0)

		distance = LB6411_distance

		neutronOutputPer100muSv = df.W[ df.distance == distance ].values

		return neutronOutputPer100muSv
# correct the dose that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
# df_LT = pd.read_csv("./MCNP/dose_lookup_table.txt", delimiter="\t")
# interpolation function
# interp_dose = interp1d(df_LT['dose_pi'], df_LT['dose_display'], kind='cubic')
#


################################################################################################################################################
################################################################################################################################################
# DASH
################################################################################################################################################
################################################################################################################################################
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
	dcc.Location(id='url', refresh=False),
	html.Div(id='page-content')
])


index_page = html.Div([
	dcc.Link('Go to live data plotter', href='/live'),
	html.Br(),
	dcc.Link('Go to historical data plotter', href='/historical'),
])


################################################################################################################################################
# LIVE route: layout
################################################################################################################################################
page_live_layout = html.Div(children=[
	html.H1(children='Neutron Generator Data Display - live plotter'),


	html.Div([
	html.Label('Plot past hours:'),
	dcc.Input(id='hours_to_plot',value='2', type='number')]),
	dcc.Interval( # timer every 10 seconds update
	id='my-interval', n_intervals=0),
	html.Label('Live plot settings:'),
    dcc.RadioItems(id='set-time',
    value=5000,
    options=[
        {'label': 'Every 5 seconds', 'value': 5000},
        {'label': 'Off', 'value': 60*60*1000} # or just every hour
    ]),
	html.Div(id='display-time'),
	html.Hr(),

	html.Div(id='display-selected-values'),
	dcc.Graph(id='indicator-graphic-live'),  # displays the data
	html.Div(id='page-live-content'),
	html.Br(),
	dcc.Link('Go to historical data plotter', href='/historical'),
	html.Br(),
	dcc.Link('Go back to home', href='/'),

])

################################################################################################################################################
# HISTORICAL route: layout
################################################################################################################################################
# gets the available dates in the database (based on data_dose)
lst_dates = getAvailableHistoricalDates()
# print(lst_dates)
page_historical_layout = html.Div([
	html.H1(children='Neutron Generator Data Display - historical plotter'),
	html.H4('Select date:'),
	html.Div(
		dcc.Dropdown(id='date_dropdown',
			options=[{'label': i, 'value': i} for i in lst_dates],
			value='2018-07-30')
		),
	html.Button(id='button-plot-historical', n_clicks=0, children='Submit'),

	html.Hr(),

	html.Div(id='display-date-plotted'),

	dcc.Graph(id='indicator-graphic-historical'),  # displays the data

	html.Div(id='page-historical-content'),
	html.Br(),
	dcc.Link('Go to live data plotter', href='/live'),
	html.Br(),
	dcc.Link('Go back to home', href='/')
])


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
			  [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/live':
		return page_live_layout
	elif pathname == '/historical':
		return page_historical_layout
	else:
		return index_page
	# You could also return a 404 "URL not found" page here


################################################################################################################################################
# LIVE callbacks
################################################################################################################################################
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

if __name__ == '__main__':
	app.run_server(debug=False, port=5000, host='0.0.0.0')
