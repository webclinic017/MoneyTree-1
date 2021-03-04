import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import flask, os

def create_dash_app(routes_pathname_prefix: str = None) -> dash.Dash:

    server = flask.Flask(__name__)
    server.secret_key = os.environ.get('secret_key', 'secret')

    df = pd.read_csv('/data/curve_data.csv')

    app = dash.Dash(__name__, server=server, routes_pathname_prefix=routes_pathname_prefix)

    app.scripts.config.serve_locally = False
    dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

    fig = px.line(x=df.datetime.values, y=df.value.values, height=390, width=600)
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    'xaxis_title': None,
    'yaxis_title': "Equity",
    },
    xaxis=dict(
        showline=True,
        showgrid=False,
        showticklabels=True,
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
            )
        ),
    yaxis=dict(
        showline=True,
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
            )
        )
    )

    app.layout = html.Div([
        dcc.Graph(id="graph", figure=fig),
        html.Div(id='structure', style={'display': 'none'})
        ], className="container")

    @app.callback(Output("structure", "children"), [Input("graph", "figure")])
    def display_structure(fig_json):
        return json.dumps(fig_json, indent=2)

    return app


# curve = pd.read_csv('curve_data.csv')

# fig = px.line(
#     x=curve.index.values, y=curve.value.values, 
#     title="equity curve", height=325
# )

# app = dash.Dash(__name__)

# app.layout = html.Div([
#     dcc.Graph(id="graph", figure=fig),
#     html.Div(id='structure', style={'display': 'none'})
# ])

# @app.callback(Output("structure", "children"), [Input("graph", "figure")])
# def display_structure(fig_json):
#     return json.dumps(fig_json, indent=2)

# app.run_server(debug=True)