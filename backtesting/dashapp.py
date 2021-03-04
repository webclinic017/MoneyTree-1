import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import flask, os

def create_dash_app(routes_pathname_prefix: str = None) -> dash.Dash:

    server = flask.Flask(__name__)
    server.secret_key = os.environ.get('secret_key', 'secret')

    df = pd.read_csv('backtesting/data/curve_data.csv')

    app = dash.Dash(__name__, server=server, routes_pathname_prefix=routes_pathname_prefix)

    app.scripts.config.serve_locally = False
    dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

    fig = go.Figure(data=go.Scatter(x=df.datetime.values, y=df.value.values,
                                mode='lines', name='equity', line_shape='linear',
                                line=dict(color='royalblue', width=2)))

    fig.update_layout({
    'autosize':True,
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    'xaxis_title': None,
    'yaxis_title': None
    },
    xaxis=dict(
        showline=True,
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        linecolor='rgb(82, 82, 82)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(255,255,255)',
            )
        ),
    yaxis=dict(
        showline=True,
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        linecolor='rgb(82, 82, 82)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(255,255,255)',
            )
        ),
    plot_bgcolor='black'
    )
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
                                xanchor='left', yanchor='bottom',
                                text='Equity Curve',
                                font=dict(family='Arial',
                                            size=16,
                                            color='rgb(255,255,255)'),
                                showarrow=False))

    fig.update_layout(annotations=annotations)

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