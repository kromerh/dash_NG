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


def MWButtonControl(sql_engine, value):
	timeNow = datetime.datetime.now()
	qry = "INSERT INTO microwave_motor_command (time_created, command, executed) VALUES (%(time)s, \"%(value)s\", 0)" % {"time": timeNow, "value": value}
	sql_engine.execute(qry)

	

# CALLBACKS

# # status of MW motor
# # Stop the microwave button
# @app.callback(
# 	Output("microwave-status-monitor", "value"),
# 	[Input("microwave-MW-button-off", "children")],
# 	[State("microwave-MW-button-on", "children")]
# )
# def mw_motor_status(status_off, status_on):
# 	status = (
# 	"-----------STATUS------------\n"
# 	+ "microwave-MW-button-off: " + str(status_off) + "\n"
# 	+ "microwave-MW-button-on: " + str(status_on) + "\n"
# 	)
# 	return status

# # Start the microwave button
# @app.callback(
# 	# Output("microwave-status-monitor", "value"),
# 	Output("microwave-MW-button-on", "children"),
# 	[Input("btn-mw-motor-on", "n_clicks")]
# )
# def btn_mw_on(n_clicks):
# 	if n_clicks:
# 		sleep(3)
# 		print(f'Starting MW, n_clicks: {n_clicks}')
# 		value = "88,800"
# 		print(f'Sending {value}')
		
# 		MWButtonControl(sql_engine, value)
				
# 		sleep(3)
# 		value = "92,1100"
# 		print(f'Sending {value}')
		
# 		MWButtonControl(sql_engine, value)
# 		status = "ON"

# 		return status


# # Stop the microwave button
# @app.callback(
# 	Output("microwave-MW-button-off", "children"),
# 	[Input("btn-mw-motor-off", "n_clicks")]
# )
# def btn_mw_off(n_clicks):
# 	if n_clicks:
# 		sleep(3)
# 		print(f'Stopping MW, n_clicks: {n_clicks}')
# 		value = "92,1100"
# 		print(f'Sending {value}')
		
# 		MWButtonControl(sql_engine, value)
				

# 		sleep(3)
# 		value = "88,800"
# 		print(f'Sending {value}')
		
# 		MWButtonControl(sql_engine, value)
# 		status = "OFF"
		
# 		return status

