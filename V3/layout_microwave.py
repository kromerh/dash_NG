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


################################################################################################################################################
# layout_base
################################################################################################################################################

layout_base = html.Div(
	[
		html.Div(
			id="container",
			children=[
				html.H2("Neutron Generator Control v3"),
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
					################################################################################################################################################
					# FLOW METER
					################################################################################################################################################
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
									value=0.0,
									min = 0,
									max = 5000,
									size=100,
									label='Setpoint (0 - 5000 mV)',
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
				################################################################################################################################################
				# MICROWAVE GENERATOR CONTROL
				################################################################################################################################################
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
							"Power",
							style={
								"textAlign": "Center",
								# "paddingTop": "2.5%",
								"marginBottom": "0.1%",
							},
						),
						html.Div(
								[
									dcc.Graph(
										id="MW-Power-graph", # t1 and t2

										style={
											"height": "254px",
											"marginLeft":"0%",
											"marginTop":"0%"
											},
									),
								],
								className='row'
						),
						html.H5(
							"Frequency",
							style={
								"textAlign": "Center",
								# "paddingTop": "2.5%",
								"marginBottom": "0.1%",
							},
						),
						html.Div(
								[
									dcc.Graph(
										id="MW-Frequency-graph", # t1 and t2

										style={
											"height": "254px",
											"marginLeft":"0%",
											"marginTop":"0%"
											},
									),
								],
								className='row'
						),
						html.Hr(),
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
								dcc.Textarea(
									id="MW-status-monitor",
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
						),


					],
					className="four columns",
					style={
						"border-radius": "5px",
						"border-width": "5px",
						"border": "1px solid rgb(216, 216, 216)",
					},
				),
				################################################################################################################################################
				# HV AND DOSE
				################################################################################################################################################
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
				dcc.Interval(id="readout-interval", interval=2000, n_intervals=0),
				dcc.Interval(id="microwave-readout-interval", interval=2000, n_intervals=0),
				html.Div(id="flow-meter-readout-start-time"), # start time of mass flow reading from database
				html.Div(id="flow-meter-readout-stop-time"), # stop time of mass flow reading from database
				html.Div(id="flow-meter-readout-command-string"), # start and stop readout of mass flow reading
				html.Div(id="flow-meter-readout-running-time"), # running readout of mass flow reading
				html.Div(id="flow-meter-setpoint-value"), # setpoint hold value
				html.Div(id='flow-meter-readout-values-state'), # Hidden div inside the app that stores the data from the live db
				html.Div(id='microwave-MW-state-values'), # Hidden div inside the app that stores if the MW states
				html.Div(id='mw-db-values'), # db values from the mw
				dcc.Interval(id="live-db-readout-interval", interval=10000, n_intervals=0), # setpoint hold value
				html.Div(id="live-db-values") # setpoint hold value
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

