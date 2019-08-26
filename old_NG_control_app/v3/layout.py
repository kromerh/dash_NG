from app import app

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

def main_layout() -> html.Div:
	return html.Div([
		dcc.Location(id='url', refresh=False),
		html.Div(id='page-content')
	])


def index_page() -> html.Div:
	return html.Div([
		dcc.Link('Go to live data plotter', href='/apps/app_live'),
		html.Br(),
		dcc.Link('Go to historical data plotter', href='/apps/app_histo'),
	])



def app_live_layout(hours_to_plot) -> html.Div:
	return html.Div(children=[
		html.Div([
		   html.H1(children='Neutron Generator Data Display - live plotter')
		   ], className='banner'),

		html.Hr(),


		dcc.Interval(id='live-plot-update', interval=5000, n_intervals=0),

		html.Div([
			html.Div([
				html.H3('Live stream for the past {} hours'.format(hours_to_plot))
				], className='Title-center-header'),

			html.Div([
				html.H3(id='display-time')
				], className='Title-center'),

			html.Div([
			   dcc.Graph(id='indicator-graphic-live-HV')
			   ], className='five columns live-plot'),  # displays HV data

			html.Div([
			   dcc.Graph(id='indicator-graphic-live-dose')
			   ], className='five columns live-plot'),  # displays Dose

		], className='row graph-row'),

		html.Hr(),

		html.Div([
			html.Div([
				html.H3('Past 12 hours of data')
				], className='Title-center-header'),
			html.Div([
				html.Button(id='button-plot-today', n_clicks=0, children='Update')
				], className='button-update-today-plot'),
			html.Div([
			   dcc.Graph(id='indicator-graphic-today')
			   ], className='ten columns live-plot'),  # displays HV data


		], className='row graph-row'),

		# Hidden div inside the app that stores the data from the live db
		html.Div(id='live-db-values', style={'display': 'none'}),

		html.Div([
			html.Div(id='page-live-content'),
			html.Br(),
			dcc.Link('Go to historical data plotter', href='/apps/app_histo'),
			html.Br(),
			dcc.Link('Go back to home', href='/'),
		]),
	])