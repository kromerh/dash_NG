# -*- coding: utf-8 -*-
import flask
import dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

app.config.suppress_callback_exceptions = True
