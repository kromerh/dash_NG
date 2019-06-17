import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash_daq import DarkThemeProvider as DarkThemeProvider
from dash.dependencies import Input, Output, State
import dash
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime
import pymysql
import datetime
import time

from app import app


state_dic = {'state': "none"}

################################################################################################################################################
# paramiko - REMOTE SSH
################################################################################################################################################
import paramiko

host="twofast-RPi3-4"
user="pi"
pwd="axfbj1122!"
paramiko.util.log_to_file('ssh.log') # sets up logging

def startFlowMeterReadout():
	print('Starting flow-meter readout...')
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.load_system_host_keys()
	client.connect(host, username=user, password=pwd)
	stdin, stdout, stderr = client.exec_command('/home/pi/Documents/flow_meter/dash_NG/flow_meter/run_readout_from_remote.sh')
	output = stdout.readlines()
	print(output)
	client.close()

def stopAllPython():
	print('Stopping all pythons...')
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.load_system_host_keys()
	client.connect(host, username=user, password=pwd)
	stdin, stdout, stderr = client.exec_command('/home/pi/Documents/flow_meter/dash_NG/flow_meter/stop_all_python.sh')
	output = stdout.readlines()
	print(output)
	client.close()



################################################################################################################################################
# function
################################################################################################################################################
def setFlowMeterControlValues(value):
	"""
	Sets the entry for the setpoint value in the database according to the user specified value
	"""
	# DOSE
	mysql_connection = pymysql.connect(host="twofast-RPi3-0",  # your host
					 user="writer",  # username
					 passwd="heiko",  # password
					 db="NG_twofast_DB", # name of the database
					 charset='utf8',
					 cursorclass=pymysql.cursors.DictCursor)


	try:
		with mysql_connection.cursor() as cursor:
			# Create a new record
			sql = "UPDATE flow_meter_control SET setpoint_voltage = (%s)"
			cursor.execute(sql, (str(value)))

		# connection is not autocommit by default. So you must commit to save
		# your changes.
		mysql_connection.commit()
		print(f'Updated setpoint_voltage {value} in flow_meter_control table.')

	finally:
		mysql_connection.close()

def readFlowMeterVoltage(pastSeconds=60): # read past 60secs by default
	"""
	Read the flow meter voltage read from the database
	"""

	db = pymysql.connect(host="twofast-RPi3-0",  # your host
						 user="doseReader",  # username
						 passwd="heiko",  # password
						 db="NG_twofast_DB",  # name of the database
						 charset='utf8',
						 cursorclass=pymysql.cursors.DictCursor)



	try:
		query = """SELECT * FROM flow_meter_readout_live ORDER BY id DESC LIMIT {}""".format(pastSeconds)
		df = pd.read_sql(query, db)


	except:
		print('Error in plotFlowMeterVoltage')


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
									style={"textAlign": "Center"},
									# className="seven columns",
								),
								# daq.StopButton(
								# 	id="start-stop",
								# 	label="D2 flow",
								# 	className="five columns",
								# 	n_clicks=0,
								# 	style={
								# 		"paddingTop": "3%",
								# 		"paddingBottom": "3%",
								# 		"display": "flex",
								# 		"justify-content": "center",
								# 		"align-items": "center",
								# 	},
								# ),
							],
							className="row",
						),
						html.Hr(),
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
							"Start Settings",
							style={
								"textAlign": "Center",
								"paddingBottom": "4.5%",
								"border-radius": "1px",
								"border-width": "5px",
								"border-bottom": "1px solid rgb(216, 216, 216)",
							},
						),
						daq.ToggleSwitch(
							id="pre-settings",
							label=["Not Set", "Set"],
							color="#FF5E5E",
							size=32,
							value=False,
							style={"marginBottom": "1%", "paddingTop": "2%"},
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
								html.H3("Gauges", style={"textAlign": "center"}),
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
										"marginLeft": "34%",
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
				dcc.Interval(id="flow-meter-readout-interval", interval=1000, n_intervals=0),
				html.Div(id="flow-meter-readout-start-time"), # start time of mass flow reading from database
				html.Div(id="flow-meter-readout-stop-time"), # stop time of mass flow reading from database
				html.Div(id="flow-meter-readout-command-string"), # start and stop readout of mass flow reading
				html.Div(id="flow-meter-readout-running-time"), # running readout of mass flow reading
				html.Div(id="flow-meter-setpoint-value"), # setpoint hold value
				html.Div(id='flow-meter-readout-values'), # Hidden div inside the app that stores the data from the live db
			],
			style={"visibility": "hidden"},
		),
	],
	style={
		"padding": "0px 10px 10px 10px",
		"marginLeft": "auto",
		"marginRight": "auto",
		"width": "1100",
		"height": "1000",
		"boxShadow": "0px 0px 5px 5px rgba(204,204,204,0.4)",
	},
)



# app.layout = root_layout


################################################################################################################################################
# callbacks
################################################################################################################################################
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

		client.close()
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
			setFlowMeterControlValues(setpoint_value)

			# set the value of the slider flow-meter-setpoint-slider"
			setpoint_value = round(setpoint_value * 1000)

			return setpoint_value
	else:
		return 2000


# callback to read the database and store in a json objective
@app.callback(
	Output('flow-meter-readout-values', 'children'),
	[Input('flow-meter-readout-interval', 'n_intervals')],
	[State("flow-meter-readout-command-string", "children")]
	)
def retrieve_data(intervals, command_string):
	# print(command_string)
	if command_string == 'START':
		 # some expensive clean data step
		 df = readFlowMeterVoltage(300)  # retrieve the past 60 seconds
		 # print('Inside retrieve_data')
		 # print(df)
		 # more generally, this line would be
		 # json.dumps(cleaned_df)
		 state_dic['state'] = 'plotting'

		 return df.to_json(date_format='iso', orient='split')
	else:
		 state_dic['state'] = 'not plotting'

# Textarea Communication
@app.callback(
	Output("flow-meter-status-monitor", "value"),
	[Input("flow-meter-readout-interval", "n_intervals")],
	[State("flow-meter-setpoint-value", "children"),
	State("flow-meter-readout-command-string", "children"),
	State("flow-meter-readout-values", "children")]
)
def flow_meter_text_area(intervals,
	flow_meter_setpoint_value,
	command_string,
	json_data
	):

	# if command_string == 'START':
	# 	startFlowMeterReadout()
	# if command_string == 'STOP':
	# 	stopAllPython()
	if state_dic['state'] == "plotting":
		# print("plotting")
		df = pd.read_json(json_data, orient='split')
		last_db_reading = df.loc[0,'time']
		# print(len(df))
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
				width=5.0
			),
			text='Voltage [V]',
			# mode='markers',
			mode='lines',
			opacity=1,
			marker={
				'size': 15,
				'line': {'width': 0.5, 'color': 'white'}
			},

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
