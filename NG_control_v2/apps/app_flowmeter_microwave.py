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


state_dic = {'state': "none"}

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

################################################################################################################################################
# function
################################################################################################################################################

# ********************
# FLOW METER
# ********************

def setFlowMeterControlValues(value, sql_engine):
	"""
	Sets the entry for the setpoint value in the database according to the user specified value
	"""
	query= "UPDATE flow_meter_control SET setpoint_voltage = %(setpoint_voltage)s" % {"setpoint_voltage": value}
	sql_engine.execute(query)

	print(f'Updated setpoint_voltage {value} in flow_meter_control table.')


def readFlowMeterVoltage(sql_engine, pastSeconds=60): # read past 60secs by default
	"""
	Read the flow meter voltage read from the database
	"""
	query = "SELECT * FROM flow_meter_readout_live ORDER BY id DESC LIMIT %(pastSeconds)s" % {"pastSeconds": pastSeconds}
	df = pd.read_sql(query, sql_engine)

	return df

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



################################################################################################################################################
# base_layout
################################################################################################################################################

base_layout = html.Div(
	[
		html.Div(
			id="container",
			children=[
				html.H2("Neutron Generator Control"),
				# html.A(
					# html.Img(
					# 	src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/excel/dash-daq/dash-daq-logo-by-plotly-stripe+copy.png"
					# ),
					# href="http://www.dashdaq.io",
				# ),
			],
			className="banner",
		),
		html.Div(
			[
				html.Div(
					[
						html.Div(
							[
								html.H3(
									"Flow Meter Control",
									style={
										"textAlign": "Center",
										"paddingBottom": "4.5%",
										"border-radius": "1px",
										"border-width": "5px",
										"border-bottom": "1px solid rgb(216, 216, 216)",
									},
								),
							],
							className="row",
						),
						html.Div(
							children=[
								html.H5(
									"Setpoint Mass Flow",
									style={
										"textAlign": "Center",
										# "paddingTop": "2.5%",
										"marginBottom": "5%",
									},
									)
							],
						),
						html.Div(
							[
								daq.NumericInput(
									id='flow-meter-setpoint-numeric-input',
									value=2.0,
									min = 0,
									max = 5,
									size=80,
									label='Setpoint (0 - 5V)',
									labelPosition='bottom'
								),
								html.Button(
									"Send",
									id='flow-meter-setpoint-button',
									style={
										"marginLeft": "5%",
										"marginRight": "5%",
										"marginBottom": "5%",
									}
								),

							],
							className="row",
							style={
								"display": "flex",
								"justify-content": "center",
								"align-items": "center",
								"marginBottom": "10%",
							},
						),
						html.Div(
							[
								daq.Slider(
									id="flow-meter-setpoint-slider",
									value=2000,
									disabled=True,
									color="#EA0606",
									min=0,
									max=5000,
									size=350,
									handleLabel={
										"showCurrentValue": "True",
										"label": "Now (mV)",
										'style': {'color': '#EA0606'}
									},
									marks={
										"0": "0",
										"1000": "",
										"2000": "",
										"3000": "",
										"4000": "",
										"5000": "5 Volt",
									},
								),

							],
							className="row",
							style={
								"display": "flex",
								"justify-content": "center",
								"align-items": "center",
								"marginBottom": "2%",
							},
						),
						html.Hr(),
						html.Div(
							[
								html.Div(
									[
										daq.StopButton(
											"Start",
											id='flow-meter-readout-start-button',
											n_clicks=0,
											style={
												"width": "20%",
												"display": "flex",
												"justify-content": "center",
												"align-items": "center",
												"marginLeft": "2%",
												"marginRight": "2%",
												"marginBottom": "5%",
											}
										),
										daq.StopButton(
											"Stop",
											id='flow-meter-readout-stop-button',
											n_clicks=0,
											style={
												"width": "20%",
												"color": "red",
												"display": "flex",
												"justify-content": "center",
												"align-items": "center",
												"marginLeft": "2%",
												"marginRight": "2%",
												"marginBottom": "5%",
											}
										)
									],
									className="three columns",
									style={"marginLeft": "13%"},
								),
								html.H5(
									"Reading Mass Flow vs. Time",
									style={
										"textAlign": "Center",
										# "marginBottom": "10%",
										# "marginTop": "10%",
									},
								)
							],
						),
						html.Div(
							dcc.Graph(
								id="flow-meter-readout-graph",
								style={
									"height": "254px",
									"marginTop": "15%",
									},
							),
						),
						html.Hr(),
						html.Div(
							children=[
								html.H5(
									"Status Monitor",
									style={"textAlign": "center"}
									)
							],
						),
						html.Div(
							[
								dcc.Textarea(
									id="flow-meter-status-monitor",
									draggable=False,
									placeholder="",
									# readOnly=True,
									value="",
									style={"width": "90%", "height": "10%", "resize": "none"},
									disabled=True,
									rows=10,
								)
							],
							style={
								"display": "flex",
								"justify-content": "center",
								"align-items": "center",

							},
						)
					],
					className="four columns",
					style={
						"border-radius": "5px",
						"border-width": "5px",
						"border": "1px solid rgb(216, 216, 216)",
					},
				),
				html.Div(
					[
						html.H3(
							"Microwave Generator Control",
							style={
								"textAlign": "Center",
								"paddingBottom": "4.5%",
								"border-radius": "1px",
								"border-width": "5px",
								"border-bottom": "1px solid rgb(216, 216, 216)",
							},
						),
						html.H5(
							"Status",
							style={
								"textAlign": "Center",
								# "paddingTop": "2.5%",
								"marginBottom": "0.1%",
							},
						),
						html.Div(
							[
								html.Div(
									[
										daq.Indicator(
											id='microwave-24V-indicator',
											value=False,
											color="red",
											label="24V Relais",
											labelPosition="bottom"
										)
									],
									className='three columns', style={'margin-left':'15%','margin-right':'-5%','margin-bottom': '5px', 'margin-top': '15px'}
									# className='two columns', style={'margin-bottom': '5px', 'margin-top': '15px'}
								),
								html.Div(
									[
										daq.Indicator(
											id='microwave-5V-indicator',
											value=False,
											color="red",
											label="5V Relais",
											labelPosition="bottom"
										),
									],
									className='two columns', style={'margin-bottom': '5px', 'margin-top': '15px'}
								),
								html.Div(
									[
										daq.Indicator(
											id='microwave-temp-indicator',
											value=False,
											color="red",
											label="Temperature",
											labelPosition="bottom"
										),
									],
									className='two columns', style={'margin-bottom': '5px', 'margin-top': '15px'}
								),
								html.Div(
									[
										daq.Indicator(
											id='microwave-D2flow-indicator',
											value=False,
											color="red",
											label="D2 flow",
											labelPosition="bottom"
										),
									],
									className='two columns', style={'margin-bottom': '5px', 'margin-top': '15px'}
								),
								html.Div(
									[
										daq.Indicator(
											id='microwave-RF-indicator',
											value=False,
											color="red",
											label="RF",
											width=35,
											height=35,
											labelPosition="bottom"
										),
									],
									className='two columns', style={'margin-bottom': '5px', 'margin-top': '15px', 'size': '10px'}
								),
							],
							className='row'
						),
						html.Hr(),
						html.Div(
							[
								daq.LEDDisplay(
									id='microwave-power-display',
									size=30,
									label="Power (W)",
									color="#447EFF",
									value=500,
									labelPosition="top",
									style={'marginRight': '7%'},
									className='three columns'
								),
								daq.LEDDisplay(
									id='microwave-frequency-display',
									size=30,
									label="Frequency (MHz)",
									color="#447EFF",
									value="2450",
									labelPosition="top",
									style={'marginBottom': '0px'},
									className='three columns'
								),
								daq.LEDDisplay(
									id='microwave-temperature1-display',
									size=10,
									label="T 1 (degC)",
									color="#447EFF",
									value="20",
									labelPosition="top",
									style={'marginTop': '10px'},
									className='three columns'
								),
								daq.LEDDisplay(
									id='microwave-temperature2-display',
									size=10,
									label="T 2 (degC)",
									color="#447EFF",
									value="20",
									labelPosition="top",
									style={'marginTop': '10px'},
									className='three columns'
								),
							],
							className='row', style={'marginLeft':"20%"}
						),
						html.Hr(),
						html.Div(
							[
								daq.PowerButton(
									id='microwave-shutdown',
									on='true',
									label="Shutdown",
									labelPosition='bottom',
									color="red",
									disabled=True,
									className='four columns'
								),
								daq.PowerButton(
									id='microwave-RF-start',
									on=False,
									label="RF ON/OFF",
									labelPosition='bottom',
									color="green",
									# disabled=True,
									className='four columns'
								),
								daq.PowerButton(
									id='microwave-DLL-start',
									on=False,
									label="DLL ON/OFF",
									labelPosition='bottom',
									color="orange",
									# disabled=True,
									className='four columns'
								),
							], className='row'
							, style={'marginLeft':"20%","marginBottom": "5.5%"}
						),
						html.Div(
							[
								html.H5(
									"Power (W)",
									className='eight columns',
									style={
										"textAlign": "Center",
										# "paddingTop": "2.5%",
									},
								),
								daq.StopButton(
									"Send",
									id='microwave-power-send-button',
									n_clicks=0,
									style={
										"width": "20%",
										"display": "flex",
										"justify-content": "center",
										"align-items": "center",
										"marginLeft": "2%",
										"marginRight": "2%",
										# "marginBottom": "5%",
									}
								),
							], className='row', style={"marginBottom": "5.5%"}
						),
						html.Div(
							[
								daq.Slider(
									id="microwave-power-slider",
									value=0,
									color="red",
									min=0,
									max=500,
									size=400,
									step=1,
									handleLabel={
										"showCurrentValue": True,
										"label": "Value"
									},
									marks={
										"0": "0",
										"100": "",
										"200": "200",
										"300": "",
										"400": "",
										"500": "500",
									},
									# targets={
									# 	"80": {
									# 		"showCurrentValue": "False",
									# 		"label": "WARNING",
									# 		"color": "#EA0606",
									# 	},
									# 	"100": "",
									# },
								)
							],
							style={
								"display": "flex",
								"justify-content": "center",
								"align-items": "center",
								"marginBottom": "12%",
							},
							className='row'
						),
						html.Div(
							[
								html.H5(
									"Frequency (MHz)",
									className='eight columns',
									style={
										"textAlign": "Center",
										# "paddingTop": "2.5%",
									},
								),
								daq.StopButton(
									"Send",
									id='microwave-frequency-send-button',
									n_clicks=0,
									style={
										"width": "20%",
										"display": "flex",
										"justify-content": "center",
										"align-items": "center",
										"marginLeft": "2%",
										"marginRight": "2%",
										# "marginBottom": "5%",
									}
								),
							], className='row', style={"marginBottom": "5.5%"}
						),
						html.Div(
							[
								daq.Slider(
									id="microwave-frequency-slider",
									value=0,
									color="red",
									min=0,
									max=2450,
									size=400,
									step=10,
									handleLabel={
										"showCurrentValue": True,
										"label": "Value"
									},
									marks={
										"0": "0",
										"500": "500",
										"1000": "1000",
										"2000": "2000",
										"2450": "2450",
									},
									# targets={
									# 	"80": {
									# 		"showCurrentValue": "False",
									# 		"label": "WARNING",
									# 		"color": "#EA0606",
									# 	},
									# 	"100": "",
									# },
								)
							],
							style={
								"display": "flex",
								"justify-content": "center",
								"align-items": "center",
								"marginBottom": "12%",
							},
							className='row'
						),
						html.Div(
							[
								dcc.Graph(
									id="microwave-power-graph", # power and reflected power

									style={
										"height": "254px",
										"marginLeft":"0%",
										"marginTop":"0%"
										},
								),
							],
							className='row'
						),
						html.Div(
							[
								dcc.Graph(
									id="microwave-frequency-graph",

									style={
										"height": "254px",
										"marginLeft":"0%",
										"marginTop":"0%"
										},
								),
							],
							className='row'
						),
						html.Div(
							[
								dcc.Graph(
									id="microwave-temperature-graph", # t1 and t2

									style={
										"height": "254px",
										"marginLeft":"0%",
										"marginTop":"0%"
										},
								),
							],
							className='row'
						),
						html.Div(
							[
								dcc.Input(
									id="acceleration-set",
									placeholder="Acceleration",
									type="text",
									value="",
									className="six columns",
									style={
										"width": "35%",
										"marginLeft": "13.87%",
										"marginTop": "3%",
									},
								),
								dcc.Input(
									id="address-set",
									placeholder="Address",
									type="text",
									value="",
									className="six columns",
									maxlength="1",
									style={"width": "35%", "marginTop": "3%"},
								),
							],
							className="row",
						),
						html.Div(
							[
								dcc.Input(
									id="baudrate",
									placeholder="Baudrate",
									type="text",
									value="",
									className="six columns",
									style={
										"width": "35%",
										"marginLeft": "13.87%",
										"marginTop": "3%",
									},
								),
								dcc.Input(
									id="com-port",
									placeholder="Port",
									type="text",
									value="",
									className="six columns",
									style={"width": "35%", "marginTop": "3%"},
								),
							],
							className="row",
						),
						html.H5(
							"Motor Current",
							style={
								"textAlign": "Center",
								"paddingTop": "2.5%",
								"marginBottom": "12%",
								"marginTop": "5%",
							},
						),
						html.Div(
							[
								daq.Slider(
									id="motor-current",
									value=30,
									color="default",
									min=0,
									max=100,
									size=250,
									step=None,
									handleLabel={
										"showCurrentValue": "True",
										"label": "VALUE",
									},
									marks={
										"0": "0",
										"10": "",
										"20": "",
										"30": "",
										"40": "",
										"50": "50",
										"60": "",
										"70": "",
										"80": "",
										"90": "",
										"100": "100",
									},
									targets={
										"80": {
											"showCurrentValue": "False",
											"label": "WARNING",
											"color": "#EA0606",
										},
										"100": "",
									},
								)
							],
							style={
								"display": "flex",
								"justify-content": "center",
								"align-items": "center",
								"marginBottom": "12%",
							},
						),
						html.H5(
							"Hold Current",
							style={"textAlign": "center", "marginBottom": "12%"},
						),
						html.Div(
							[
								daq.Slider(
									id="hold-current",
									color="default",
									value=20,
									min=0,
									max=100,
									size=250,
									step=None,
									handleLabel={
										"showCurrentValue": "True",
										"label": "VALUE",
									},
									marks={
										"0": "0",
										"10": "",
										"20": "",
										"30": "",
										"40": "",
										"50": "50",
										"60": "",
										"70": "",
										"80": "",
										"90": "",
										"100": "100",
									},
									targets={
										"80": {
											"showCurrentValue": "False",
											"label": "WARNING",
											"color": "#EA0606",
										},
										"100": "",
									},
								)
							],
							style={
								"display": "flex",
								"justify-content": "center",
								"align-items": "center",
								"marginBottom": "12%",
							},
						),
						html.H5(
							"Step Size",
							style={"textAlign": "Center", "marginBottom": "12%"},
						),
						html.Div(
							[
								daq.Slider(
									id="step-size",
									value=64,
									color="default",
									min=1,
									max=256,
									size=250,
									step=None,
									handleLabel={
										"showCurrentValue": "True",
										"label": "VALUE",
									},
									marks={
										"1": "1",
										"2": "",
										"4": "",
										"8": "",
										"16": "",
										"32": "",
										"64": "",
										"128": "128",
										"256": "256",
									},
								)
							],
							style={
								"display": "flex",
								"justify-content": "center",
								"align-items": "center",
								"marginBottom": "12%",
							},
						),
						html.Div(
							[
								daq.ColorPicker(
									id="color-picker",
									label="Color Picker",
									value=dict(hex="#119DFF"),
									size=150,
								)
							],
							style={
								"border-radius": "1px",
								"border-width": "5px",
								"border-top": "1px solid rgb(216, 216, 216)",
								"paddingTop": "5%",
								"paddingBottom": "5%",
							},
						),
					],
					className="four columns",
					style={
						"border-radius": "5px",
						"border-width": "5px",
						"border": "1px solid rgb(216, 216, 216)",
					},
				),
				html.Div(
					[
						html.Div(
							[
								html.H3("HV and Dose", style={"textAlign": "center"}),
								html.Div(
									[
										dcc.Graph(
											id="HV-graph", # t1 and t2

											style={
												"height": "254px",
												"marginLeft":"0%",
												"marginTop":"0%"
												},
										),
									],
									className='row'
								),
								html.Div(
									[
										dcc.Graph(
											id="Dose-graph", # t1 and t2

											style={
												"height": "254px",
												"marginLeft":"0%",
												"marginTop":"0%"
												},
										),
									],
									className='row'
								),
								html.Div(
									[
										dcc.Graph(
											id="position-gauge",
											className="six columns",
											style={
												"marginLeft": "20%",
												"display": "flex",
												"justify-content": "right",
												"align-items": "right",
											},
										)
									],
									className="row",
									style={
										"border-radius": "1px",
										"border-width": "5px",
										"border-top": "1px solid rgb(216, 216, 216)",
										"marginBottom": "4%",
									},
								),
								html.P("Velocity Mode", style={"textAlign": "center"}),
								html.Div(
									[
										html.Div(
											[
												html.Div(
													[
														html.Div(
															id="rotate-graph",
															style={
																"transform": "rotate(50deg)"
															},
															children=[
																html.H2(
																	"|",
																	style={
																		"width": "10px",
																		"height": "10px",
																		"background-color": "yellow",
																	},
																)
															],
														)
													],
													style={
														"width": "10px",
														"height": "10px",
													},
												)
											],
											style={
												"paddingLeft": "48%",
												"paddingTop": "25%",
												"paddingBottom": "45%",
												"border-radius": "5px",
											},
										)
									],
									style={
										"border-width": "5px",
										"border": "1px solid rgb(216, 216, 216)",
										"border-radius": "5px",
										"width": "29%",
										"height": "10%",
										# "marginLeft": "34%",
										"marginLeft": "3%",
										"marginBottom": "6%",
									},
								),
								html.Div(
									[
										daq.Gauge(
											id="speed-gauge",
											showCurrentValue=True,
											units="Revolutions/Second",
											min=0,
											max=3,
											value=0,
											size=150,
											color="#FF5E5E",
											label="Revolutions Per Second (Max 3 RPS)",
											className="twelve columns",
											style={
												"marginTop": "5%",
												"marginBottom": "-10%",
												"color": "#222",
											},
										)
									],
									className="row",
									style={
										"border-radius": "1px",
										"border-width": "5px",
										"border-top": "1px solid rgb(216, 216, 216)",
									},
								),
							],
							style={
								"border-radius": "5px",
								"border-width": "5px",
								"border": "1px solid rgb(216, 216, 216)",
							},
						)
					],
					className="four columns",
				),
			],
			className="row",
		),
		# Placeholder Divs
		html.Div(
			[
				dcc.Interval(id="readout-interval", interval=1000, n_intervals=0),
				html.Div(id="flow-meter-readout-start-time"), # start time of mass flow reading from database
				html.Div(id="flow-meter-readout-stop-time"), # stop time of mass flow reading from database
				html.Div(id="flow-meter-readout-command-string"), # start and stop readout of mass flow reading
				html.Div(id="flow-meter-readout-running-time"), # running readout of mass flow reading
				html.Div(id="flow-meter-setpoint-value"), # setpoint hold value
				html.Div(id='flow-meter-readout-values'), # Hidden div inside the app that stores the data from the live db
				html.Div(id='microwave-temperature-values'), # Hidden div inside the app that stores the temperature data
				html.Div(id='microwave-state-values'), # state of the relais 24, relais 5, and rf
			],
			style={"visibility": "hidden"},
		),
	],
	style={
		"padding": "0px 5px 5px 5px",
		"marginLeft": "0%",
		"marginRight": "0%",
		"width": "1100",
		"height": "1000",
		"boxShadow": "0px 0px 5px 5px rgba(204,204,204,0.4)",
	},
)



# app.layout = root_layout


################################################################################################################################################
# callbacks
################################################################################################################################################
# ********************************
# FLOW METER
# ********************************

# Start  the flow meter readout from the database
@app.callback(
	Output("flow-meter-readout-start-time", "children"),
	[Input("flow-meter-readout-start-button", "n_clicks")]
)
def flow_meter_start_readout(n_clicks):
	# print('start')
	# print(n_clicks)
	if n_clicks >= 1:
		return time.time()
	return 0.0

# Stop the flow meter readout from the database
@app.callback(
	Output("flow-meter-readout-stop-time", "children"),
	[Input("flow-meter-readout-stop-button", "n_clicks")]
)
def flow_meter_stop_readout(n_clicks):
	# print('stop')
	# print(n_clicks)
	if n_clicks >= 1:
		return time.time()
	return 1.0

# Button Control Panel
@app.callback(
	Output("flow-meter-readout-command-string", "children"),
	[Input("flow-meter-readout-start-time", "children"),
	Input("flow-meter-readout-stop-time", "children")]
)
def command_string(start, stop):
	master_command = {
		"START": start,
		"STOP": stop,
	}
	# print(master_command)
	recent_command = max(master_command, key=master_command.get)
	return recent_command


# Setpoint mass flow, store in hold
@app.callback(
	Output("flow-meter-setpoint-value", "children"),
	[Input("flow-meter-setpoint-numeric-input", "value")]
)
def flow_meter_setpoint_to_hold(setpoint_value):
	# print(setpoint_value)
	return setpoint_value

# Send hold setpoint mass flow to RPi
@app.callback(
	Output("flow-meter-setpoint-slider", "value"),
	[Input("flow-meter-setpoint-button", "n_clicks")],
	[State("flow-meter-setpoint-value", "children")]
)
def flow_meter_setpoint_button(n_clicks, setpoint_value):
	if n_clicks:
		print(f'Inside flow_meter_setpoint_button, n_clicks is {n_clicks}, setpoint_value is {setpoint_value}')
		#sanity check that it is between 0 and 5
		if (setpoint_value > 0.0) & (setpoint_value < 5.0):

			# update field in the database
			setFlowMeterControlValues(setpoint_value, sql_engine)

			# set the value of the slider flow-meter-setpoint-slider"
			setpoint_value = round(setpoint_value * 1000)

			return setpoint_value
	else:
		return 2000


# callback to read the database and store in a json objective
@app.callback(
	Output('flow-meter-readout-values', 'children'),
	[Input('readout-interval', 'n_intervals')],
	[State("flow-meter-readout-command-string", "children")]
	)
def retrieve_data(intervals, command_string):
	print(state_dic)
	if command_string == 'START':

		df = readFlowMeterVoltage(sql_engine, 300)  # retrieve the past 60 seconds
		state_dic['state'] = 'plotting'

		return df.to_json(date_format='iso', orient='split')
	else:
		 state_dic['state'] = 'not plotting'

# Textarea Communication
@app.callback(
	Output("flow-meter-status-monitor", "value"),
	[Input("readout-interval", "n_intervals")],
	[State("flow-meter-setpoint-value", "children"),
	State("flow-meter-readout-command-string", "children"),
	State("flow-meter-readout-values", "children")]
)
def flow_meter_text_area(intervals,
	flow_meter_setpoint_value,
	command_string,
	json_data
	):
	if state_dic['state'] == "plotting":
		# print("plotting")
		df = pd.read_json(json_data, orient='split')
		last_db_reading = df.loc[0,'time']
		last_db_reading = pd.to_datetime(last_db_reading)
		last_db_reading = last_db_reading.strftime("%Y-%m-%d, %H:%M:%S")
	else:
		last_db_reading = -1


	status = (
		"-----------STATUS------------\n"
		+ "Readout status: " + str(command_string) + "\n"
		+ "Last reading mass flow received: " + str(last_db_reading) + "\n"
		+ "flow_meter_setpoint_value: " + str(flow_meter_setpoint_value) + " V"
	)

	return status


# Flow meter Graph
@app.callback(
	Output("flow-meter-readout-graph", "figure"),
	[Input("flow-meter-readout-values", "children")]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def plot_graph_data(json_data):

	print(state_dic)
	traces = []

	try:
		df = pd.read_json(json_data, orient='split')
		print('inside plot_graph_data, read df')
		# print(df.iloc[0,:])
		traces.append(go.Scatter(
			x=df['time'],
			y=df['read_voltage'],
			line=go.scatter.Line(
				color='#42C4F7',
				# width=2.0
			),
			text='Voltage [V]',
			# mode='markers',
			mode='lines+markers',
			opacity=1,

			name='Voltage [V]'
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
			yaxis={'title': 'Voltage [V]'},
			margin={'l': 100, 'b': 100, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}

# ********************************
# MICROWAVE
# ********************************



# STAUTS CONTROL: Coloring the LEDs


# Read the states from the database
@app.callback(
	Output("microwave-state-values", "children"),
	[Input("readout-interval", "n_intervals")]
)
def microwave_set_state_relais_24(n_intervals):
	# call the function to read the state df
	df = getState(sql_engine)

	return df

# Color 24V relais red or green depending on its state
@app.callback(
	Output("microwave-24V-indicator", "color"),
	[Input("microwave-state-values", "children")]
)
def microwave_color_relais_24(df):
	# check if the last entries in the relais 24 column are majority 1, then return 1 for green otherwise 0 for red
	vals = df['relais_24'].value_counts()
	if vals[1] > vals[0]:
		return "green"
	else:
		return "red"


# Color 5V relais red or green depending on its state
@app.callback(
	Output("microwave-5V-indicator", "color"),
	[Input("microwave-state-values", "children")]
)
def microwave_color_relais_5(df):
	# check if the last entries in the relais 5 column are majority 1, then return 1 for green otherwise 0 for red
	vals = df['relais_5'].value_counts()
	if vals[1] > vals[0]:
		return "green"
	else:
		return "red"

# Color rf relais red or green depending on its state
@app.callback(
	Output("microwave-RF-indicator", "color"),
	[Input("microwave-state-values", "children")]
)
def microwave_color_relais_rf(df):
	# check if the last entries in the relais 5 column are majority 1, then return 1 for green otherwise 0 for red
	vals = df['rf_status'].value_counts()
	if vals[1] > vals[0]:
		return "green"
	else:
		return "red"




# # Color temperature red or green depending on its state
# @app.callback(
# 	Output("microwave-state-temperature", "children"),
# 	[Input("readout-interval", "n_intervals")]
# )
# def microwave_set_state_relais_5(n_intervals):
# 	# call the function to read the state df
# 	df = getState(sql_engine)

# 	# check if the last entries in the relais 24 column are majority 1, then return 1 for green otherwise 0 for red
# 	vals = df['relais_5'].value_counts()
# 	if vals[1] > vals[0]:
# 		return 1 # green
# 	else:
# 		return 0 # red

# # Color 5V relais red or green depending on its state
# @app.callback(
# 	Output("microwave-5V-indicator", "color"),
# 	[Input("microwave-state-relais-5", "children")]
# )
# def microwave_color_relais_5(state_relais_5):
# 	if state_relais_5 == 1:
# 		return "green"
# 	else:
# 		return "red"



