import sys
sys.path.append("./")

import config, sqlite3, dash, json
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from backtesting.data import create_dataframes
import dash_table

from flask import Flask

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dash/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
        ]
    )

    # Load data
    conn = sqlite3.connect(config.DB_FILE)
    curve_df, buynhold_df, return_df = create_dataframes(conn)

    # Create Dash Layout
    # Equity Curve
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=curve_df.datetime.values, y=curve_df.value.values,
                            mode='lines', name='equity', line_shape='linear',
                            line=dict(color='rgb(96,236,39,1)', width=3)))

    fig.add_trace(go.Scatter(x=buynhold_df.datetime.values, y=buynhold_df.value.values,
                            mode='lines', name='buynhold', line_shape='linear',
                            line=dict(color='rgb(189,189,189)', width=1)))

    fig.add_trace(go.Scatter(x=curve_df.datetime.values, y=curve_df.dotted.values,
                            mode='lines', name='breakeven', line_shape='linear',
                            line=dict(color='white', width=2, dash='dot')))

    fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(
            family="Arial",
            size=12,
            color="white"
        )
    ))

    fig.update_yaxes(title="Net Asset Value", title_font=dict(size=14, family='Arial', color='white'))

    fig.update_layout({
    'autosize':True,
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    'xaxis_title': None
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

    # Returns
    fig2 = go.Figure()

    fig2.add_trace(
    go.Bar(name='Return',
            x=return_df['datetime'],
            y=return_df['value'],
            marker_color = return_df['color']
        ))

    fig2.update_layout(barmode='stack')

    fig2.update_yaxes(title="Return (%)", title_font=dict(size=14, family='Arial', color='white'))

    fig2.update_layout({
    'autosize':True,
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    'xaxis_title': None
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
    zeroline=True,
    zerolinecolor='white',
    zerolinewidth=2,
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
                            text='Returns',
                            font=dict(family='Arial',
                                        size=16,
                                        color='rgb(255,255,255)'),
                            showarrow=False))

    fig2.update_layout(annotations=annotations)

    dash_app.layout = html.Div([
        dcc.Interval('graph-update', interval = 20000, n_intervals = 0),
        dcc.Graph(
            id='equity',
            figure=fig
        ),
        html.Div([dash_table.DataTable(
            id='equity_tbl',
            columns = [{"name": i, "id": i} for i in curve_df.columns],
            data = curve_df.to_dict('records')
        )], style = {'display':'none'}),
        dcc.Graph(
            id='returns',
            figure=fig2
        ),
        html.Div([dash_table.DataTable(
            id='returns_tbl',
            columns = [{"name": i, "id": i} for i in return_df.columns],
            data = return_df.to_dict('records')
        )], style = {'display':'none'})
    ], className="container")

    # Find syntax for a callback where I can refresh the curve_df and return_df.
    @dash_app.callback(
            dash.dependencies.Output('equity_tbl','data'),
            [dash.dependencies.Input('graph-update', 'n_intervals')])
    def updateTable(n):

        conn = sqlite3.connect(config.DB_FILE)
        curve_df, buynhold_df, return_df = create_dataframes(conn)

        return curve_df.to_dict('records')

    @dash_app.callback(Output('equity', 'figure'),Input('equity_tbl', 'data'))
    def update_figure(n):

        # Load data
        conn = sqlite3.connect(config.DB_FILE)
        curve_df, buynhold_df, return_df = create_dataframes(conn)

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=curve_df.datetime.values, y=curve_df.value.values,
                                mode='lines', name='equity', line_shape='linear',
                                line=dict(color='rgb(96,236,39,1)', width=3)))

        fig.add_trace(go.Scatter(x=buynhold_df.datetime.values, y=buynhold_df.value.values,
                                mode='lines', name='buynhold', line_shape='linear',
                                line=dict(color='rgb(189,189,189)', width=1)))

        fig.add_trace(go.Scatter(x=curve_df.datetime.values, y=curve_df.dotted.values,
                                mode='lines', name='breakeven', line_shape='linear',
                                line=dict(color='white', width=2, dash='dot')))

        fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                family="Arial",
                size=12,
                color="white"
            )
        ))

        fig.update_yaxes(title="Net Asset Value", title_font=dict(size=14, family='Arial', color='white'))

        fig.update_layout({
        'autosize':True,
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'xaxis_title': None
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

        return fig

    @dash_app.callback(Output('returns', 'figure'),Input('returns_tbl', 'data'))
    def update_figure(n):

        # Load data
        conn = sqlite3.connect(config.DB_FILE)
        curve_df, buynhold_df, return_df = create_dataframes(conn)

        # Returns
        fig2 = go.Figure()

        fig2.add_trace(
        go.Bar(name='Return',
                x=return_df['datetime'],
                y=return_df['value'],
                marker_color = return_df['color']
            ))

        fig2.update_layout(barmode='stack')

        fig2.update_yaxes(title="Return (%)", title_font=dict(size=14, family='Arial', color='white'))

        fig2.update_layout({
        'autosize':True,
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'xaxis_title': None
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
        zeroline=True,
        zerolinecolor='white',
        zerolinewidth=2,
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
                                text='Returns',
                                font=dict(family='Arial',
                                            size=16,
                                            color='rgb(255,255,255)'),
                                showarrow=False))

        fig2.update_layout(annotations=annotations)

        return fig2

    return dash_app.server

# def init_callbacks(dash_app):
#     @app.callback(Output("structure", "children"), [Input("equity", "figure"),Input("returns", "figure")])
#     def display_structure(fig_json,fig2_json):
#         return json.dumps(fig_json.update(fig2_json), indent=2)

# TEST
# app = Flask(__name__, instance_relative_config=False)

# with app.app_context():
#     # Import parts of our core Flask app
#     # from . import main

#     # Import Dash application
#     app = init_dashboard(app)
