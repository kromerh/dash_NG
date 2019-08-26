# -*- coding: utf-8 -*-
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


from app import app # calls the app
from apps import app_live, app_histo

# Dash CSS
from layout import main_layout, index_page

app.layout = main_layout()

index_page = index_page()

# callbacks
from callbacks import display_page

# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


if __name__ == '__main__':
	app.run_server(debug=True, port=5000, host='0.0.0.0')
