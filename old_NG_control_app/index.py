# -*- coding: utf-8 -*-
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


from app import app # calls the app
from apps import app_live, app_histo

# Dash CSS


# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div([
	dcc.Location(id='url', refresh=False),
	html.Div(id='page-content')
])


index_page = html.Div([
	dcc.Link('Go to live data plotter', href='/apps/app_live'),
	html.Br(),
	dcc.Link('Go to historical data plotter', href='/apps/app_histo'),
])

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
			  [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/apps/app_live':
		return app_live.layout
	elif pathname == '/apps/app_histo':
		return app_histo.layout
	else:
		return index_page
	# You could also return a 404 "URL not found" page here

if __name__ == '__main__':
	app.run_server(debug=True, port=5000, host='0.0.0.0')
