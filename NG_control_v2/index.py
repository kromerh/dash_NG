# -*- coding: utf-8 -*-
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


from app import app # calls the app
from apps import app_flowmeter_microwave

# Dash CSS


# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div([
	dcc.Location(id='url', refresh=False),
	html.Div(id='page-content')
])


index_page = html.Div([
	dcc.Link('Go to flow meter and microwave control layout', href='/apps/app_flowmeter_microwave'),
	html.Br()
])

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
			  [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/apps/app_flow_meter':
		return app_flow_meter.base_layout
	else:
		return index_page
	# You could also return a 404 "URL not found" page here

if __name__ == '__main__':
	# app.run_server(debug=False, port=5000, host='0.0.0.0')
	app.run_server(debug=True)
