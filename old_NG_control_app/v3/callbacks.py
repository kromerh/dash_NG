from app import app

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from layout import main_layout, index_page
from apps import app_live, app_histo

index_page = index_page()

# Update the index
@app.callback(Output('page-content', 'children'),
			  [Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/apps/app_live':
		return app_live.layout
	elif pathname == '/apps/app_histo':
		return app_histo.layout
	else:
		return index_page
	# You could also return a 404 "URL not found" page here
