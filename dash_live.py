# TODO: 

# * Enable plotting of historical data
# * include a tool to select how much time in the past should be collected
# * connect to db in file, no info in script!
# * enable plotting of neutron output
# * enable plotting of pressure
# * maybe: add export function
# shared x plot! https://plot.ly/python/subplots/#subplots-with-shared-xaxes


# DONE
# D Include dose lookup table in subfolder
# D Include MCNP files in subfolder

# -*- coding: utf-8 -*-
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import pymysql
from scipy.interpolate import interp1d
import plotly.graph_objs as go

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

dataset = ['live', 'historical']


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
df_LT = pd.read_csv("./MCNP/dose_lookup_table.txt", delimiter="\t")
# interpolation function
interp_dose = interp1d(df_LT['dose_pi'], df_LT['dose_display'], kind='cubic')

# HISTORICAL DATA selected
# 1.) Connect to historical data mysql, retrieve the dates as a list
# 2.) Fill the dropdown list with dates values 


# LIVE DATA selected
# 1.) Connect to live data mysql
# 2.) Display text for the last timestamp
# 3.) Plot
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
		df_dose = pd.DataFrame( [[ij for ij in i] for i in rows] )
		# voltage_dose, counts_WS, counts_BS, counts_DF
		df_dose.rename(columns={0: 'ID', 1: 'date', 2: 'dose_voltage', 3: 'HV_current', 4: 'HV_voltage'}, inplace=True)
		df_dose = df_dose.set_index(['ID'])
		df_dose['dose'] = df_dose['dose_voltage'] * 3000 / 5.5  # conversion factors according to current output signal muSv/hr
		df_dose['dose_corr'] = interp_dose(df_dose['dose'])  # uses the lookup table
		
		
		
		# HV POWER SUPPLY
		cur.execute("""SELECT * FROM HBox_Uno ORDER BY id DESC LIMIT {}""".format(pastSeconds))
		rows = cur.fetchall()
		df_HV = pd.DataFrame( [[ij for ij in i] for i in rows] )
		# voltage_dose, counts_WS, counts_BS, counts_DF
		df_HV.rename(columns={0: 'ID', 1: 'date', 2: 'dose_voltage', 3: 'HV_current', 4: 'HV_voltage'}, inplace=True)
		df_HV = df_HV.set_index(['ID'])
		df_HV['HV_current'] = df_HV['HV_current']  # mA
		df_HV['HV_voltage'] = df_HV['HV_voltage']  # kV
		# print(df_HV.head())

		# PRESSURE
		cur.execute("""SELECT * FROM BBox ORDER BY id DESC LIMIT {}""".format(pastSeconds))
		rows = cur.fetchall()
		df_pressure = pd.DataFrame( [[ij for ij in i] for i in rows] )
		df_pressure.rename(columns={0: 'ID', 1: 'date', 2: 'voltage_IS', 3: 'voltage_VC'}, inplace=True)
		df_pressure = df_pressure.set_index(['ID'])
		df_pressure['pressure_IS'] = 10**(1.667*df_pressure['voltage_IS']-11.33)
		df_pressure['pressure_VC'] = 10**(1.667*df_pressure['voltage_VC']-11.33)
		# print(df_pressure.head())

	except:
		cur.rollback()

	cur.close()

	return df_dose, df_HV, df_pressure  # df_dose contains the neutron output!




@server.route("/live")
app.layout = html.Div(children=[
	html.H1(children='Neutron Generator Data Display'),


	html.Div([
	html.H4('Select live or historical (before 3 a.m.) data:'),
	html.Label('Plot past hours:'),
    dcc.Input(id='hours_to_plot',value='2', type='number')])


	html.Hr(),


	html.Div(id='display-selected-values'),

	dcc.Graph(id='indicator-graphic')  # displays the data
])




# test callback: show which radiobutton live or historical was selected
@app.callback(
	dash.dependencies.Output('display-selected-values', 'children'),
	[dash.dependencies.Input('hours_to_plot', 'value')])
def set_cities_options(hours_to_plot):
	return u'Plotting past {} seconds...'.format(hours_to_plot*3600)


# callback to retrieve the data and plot it
@app.callback(
	dash.dependencies.Output('indicator-graphic', 'figure'),
	[dash.dependencies.Input('hours_to_plot', 'value')])
def update_figure(hours_to_plot):
	t = hours_to_plot * 3600
	df_dose, df_HV, df_pressure = retrieveLiveData(t)  # retrieve the past 2 hrs
	# plot each
	# set a common x axis label!
	traces = []
	# DOSE
	traces.append(go.Scatter(
		x=df_dose['date'],
		y=df_dose['dose_corr']/10,
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
		x=df_HV['date'],
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
		x=df_HV['date'],
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



# @app.callback(
#     dash.dependencies.Output('display-selected-values', 'children'),
#     [dash.dependencies.Input('countries-dropdown', 'value'),
#      dash.dependencies.Input('cities-dropdown', 'value')])
# def set_display_children(selected_country, selected_city):
#     return u'{} is a city in {}'.format(
#         selected_city, selected_country,
#     )


if __name__ == '__main__':
	app.run_server(debug=True, port=5000, host='0.0.0.0')
	app.run_server(debug=True)
