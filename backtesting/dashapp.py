# Working on a new version

# import json

# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import plotly.graph_objects as go
# import plotly.express as px
# import pandas as pd
# import numpy as np
# import flask, os

# def create_dash_app(curve_df, buynhold_df, return_df, routes_pathname_prefix: str = None) -> dash.Dash:

#     server = flask.Flask(__name__)
#     server.secret_key = os.environ.get('secret_key', 'secret')

#     return_df["color"] = np.where(return_df["close"]<0, 'crimson', 'rgb(96,236,39,1)')

#     app = dash.Dash(__name__, server=server, routes_pathname_prefix=routes_pathname_prefix)

#     app.scripts.config.serve_locally = True
#     dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

#     # Equity Curve
#     fig = go.Figure()

#     fig.add_trace(go.Scatter(x=curve_df.datetime.values, y=curve_df.value.values,
#                             mode='lines', name='equity', line_shape='linear',
#                             line=dict(color='rgb(96,236,39,1)', width=3)))

#     fig.add_trace(go.Scatter(x=buynhold_df.datetime.values, y=buynhold_df.value.values,
#                             mode='lines', name='buynhold', line_shape='linear',
#                             line=dict(color='rgb(189,189,189)', width=1)))

#     fig.add_trace(go.Scatter(x=curve_df.datetime.values, y=curve_df.dotted.values,
#                             mode='lines', name='breakeven', line_shape='linear',
#                             line=dict(color='white', width=2, dash='dot')))

#     fig.update_layout(
#     legend=dict(
#         orientation="h",
#         yanchor="bottom",
#         y=1.02,
#         xanchor="right",
#         x=1,
#         font=dict(
#             family="Arial",
#             size=12,
#             color="white"
#         )
#     ))

#     fig.update_yaxes(title="Net Asset Value", title_font=dict(size=14, family='Arial', color='white'))

#     fig.update_layout({
#     'autosize':True,
#     'paper_bgcolor': 'rgba(0, 0, 0, 0)',
#     'xaxis_title': None
#     },
#     xaxis=dict(
#     showline=True,
#     showgrid=False,
#     zeroline=False,
#     showticklabels=True,
#     linecolor='rgb(82, 82, 82)',
#     linewidth=2,
#     ticks='outside',
#     tickfont=dict(
#         family='Arial',
#         size=12,
#         color='rgb(255,255,255)',
#         )
#     ),
#     yaxis=dict(
#     showline=True,
#     showgrid=False,
#     zeroline=False,
#     showticklabels=True,
#     linecolor='rgb(82, 82, 82)',
#     linewidth=2,
#     ticks='outside',
#     tickfont=dict(
#         family='Arial',
#         size=12,
#         color='rgb(255,255,255)',
#         )
#     ),
#     plot_bgcolor='black'
#     )
#     annotations = []
#     annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
#                             xanchor='left', yanchor='bottom',
#                             text='Equity Curve',
#                             font=dict(family='Arial',
#                                         size=16,
#                                         color='rgb(255,255,255)'),
#                             showarrow=False))

#     fig.update_layout(annotations=annotations)

#     # Returns
#     fig2 = go.Figure()

#     fig2.add_trace(
#     go.Bar(name='Return',
#             x=return_df['datetime'],
#             y=return_df['close'],
#             marker_color = return_df['color']
#         ))

#     fig2.update_layout(barmode='stack')

#     fig2.update_yaxes(title="Return (%)", title_font=dict(size=14, family='Arial', color='white'))

#     fig2.update_layout({
#     'autosize':True,
#     'paper_bgcolor': 'rgba(0, 0, 0, 0)',
#     'xaxis_title': None
#     },
#     xaxis=dict(
#     showline=True,
#     showgrid=False,
#     zeroline=False,
#     showticklabels=True,
#     linecolor='rgb(82, 82, 82)',
#     linewidth=2,
#     ticks='outside',
#     tickfont=dict(
#         family='Arial',
#         size=12,
#         color='rgb(255,255,255)',
#         )
#     ),
#     yaxis=dict(
#     showline=True,
#     showgrid=False,
#     zeroline=True,
#     zerolinecolor='white',
#     zerolinewidth=2,
#     showticklabels=True,
#     linecolor='rgb(82, 82, 82)',
#     linewidth=2,
#     ticks='outside',
#     tickfont=dict(
#         family='Arial',
#         size=12,
#         color='rgb(255,255,255)',
#         )
#     ),
#     plot_bgcolor='black'
#     )
#     annotations = []
#     annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
#                             xanchor='left', yanchor='bottom',
#                             text='Returns',
#                             font=dict(family='Arial',
#                                         size=16,
#                                         color='rgb(255,255,255)'),
#                             showarrow=False))

#     fig2.update_layout(annotations=annotations)

#     app.layout = html.Div([
#         dcc.Graph(
#             id='equity',
#             figure=fig
#         ),
#         dcc.Graph(
#             id='returns',
#             figure=fig2
#         ),
#         html.Div(id='structure', style={'display': 'none'}),
#     ], className="container")

#     @app.callback(Output("structure", "children"), [Input("equity", "figure"),Input("returns", "figure")])
#     def display_structure(fig_json,fig2_json):
#         return json.dumps(fig_json.update(fig2_json), indent=2)


#     return app







# # # Test Run. Comment out for output to work on web app.

# curve_df = pd.read_csv('backtesting/data/curve_data.csv')
# curve_df['dotted'] = 100
# buynhold_df = pd.read_csv('backtesting/data/buynhold_data.csv')

# return_df = pd.read_csv('backtesting/data/return_data.csv')
# return_df = return_df.rename(columns = {"Unnamed: 0":"datetime"})

# return_df["color"] = np.where(return_df["close"]<0, 'crimson', 'rgb(96,236,39,1)')

# app = dash.Dash(__name__)

# app.scripts.config.serve_locally = True
# dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

# # Equity Curve
# fig = go.Figure()

# fig.add_trace(go.Scatter(x=curve_df.datetime.values, y=curve_df.value.values,
#                         mode='lines', name='equity', line_shape='linear',
#                         line=dict(color='rgb(96,236,39,1)', width=3)))

# fig.add_trace(go.Scatter(x=buynhold_df.datetime.values, y=buynhold_df.open.values,
#                         mode='lines', name='buynhold', line_shape='linear',
#                         line=dict(color='rgb(189,189,189)', width=1)))

# fig.add_trace(go.Scatter(x=curve_df.datetime.values, y=curve_df.dotted.values,
#                         mode='lines', name='breakeven', line_shape='linear',
#                         line=dict(color='white', width=2, dash='dot')))

# fig.update_layout(
# legend=dict(
#     orientation="h",
#     yanchor="bottom",
#     y=1.02,
#     xanchor="right",
#     x=1,
#     font=dict(
#         family="Arial",
#         size=12,
#         color="white"
#     )
# ))

# fig.update_yaxes(title="Net Asset Value", title_font=dict(size=14, family='Arial', color='white'))

# fig.update_layout({
# 'autosize':True,
# 'paper_bgcolor': 'rgba(0, 0, 0, 0)',
# 'xaxis_title': None
# },
# xaxis=dict(
# showline=True,
# showgrid=False,
# zeroline=False,
# showticklabels=True,
# linecolor='rgb(82, 82, 82)',
# linewidth=2,
# ticks='outside',
# tickfont=dict(
#     family='Arial',
#     size=12,
#     color='rgb(255,255,255)',
#     )
# ),
# yaxis=dict(
# showline=True,
# showgrid=False,
# zeroline=False,
# showticklabels=True,
# linecolor='rgb(82, 82, 82)',
# linewidth=2,
# ticks='outside',
# tickfont=dict(
#     family='Arial',
#     size=12,
#     color='rgb(255,255,255)',
#     )
# ),
# plot_bgcolor='black'
# )
# annotations = []
# annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
#                         xanchor='left', yanchor='bottom',
#                         text='Equity Curve',
#                         font=dict(family='Arial',
#                                     size=16,
#                                     color='rgb(255,255,255)'),
#                         showarrow=False))

# fig.update_layout(annotations=annotations)

# # Returns
# fig2 = go.Figure()

# fig2.add_trace(
# go.Bar(name='Return',
#         x=return_df['datetime'],
#         y=return_df['close'],
#         marker_color = return_df['color']
#     ))

# fig2.update_layout(barmode='stack')

# fig2.update_yaxes(title="Return (%)", title_font=dict(size=14, family='Arial', color='white'))

# fig2.update_layout({
# 'autosize':True,
# 'paper_bgcolor': 'rgba(0, 0, 0, 0)',
# 'xaxis_title': None
# },
# xaxis=dict(
# showline=True,
# showgrid=False,
# zeroline=False,
# showticklabels=True,
# linecolor='rgb(82, 82, 82)',
# linewidth=2,
# ticks='outside',
# tickfont=dict(
#     family='Arial',
#     size=12,
#     color='rgb(255,255,255)',
#     )
# ),
# yaxis=dict(
# showline=True,
# showgrid=False,
# zeroline=True,
# zerolinecolor='white',
# zerolinewidth=2,
# showticklabels=True,
# linecolor='rgb(82, 82, 82)',
# linewidth=2,
# ticks='outside',
# tickfont=dict(
#     family='Arial',
#     size=12,
#     color='rgb(255,255,255)',
#     )
# ),
# plot_bgcolor='black'
# )
# annotations = []
# annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
#                         xanchor='left', yanchor='bottom',
#                         text='Returns',
#                         font=dict(family='Arial',
#                                     size=16,
#                                     color='rgb(255,255,255)'),
#                         showarrow=False))

# fig2.update_layout(annotations=annotations)

# app.layout = html.Div(children=[
# html.Div([
#     dcc.Graph(
#         id='equity',
#         figure=fig
#     ),
#     dcc.Graph(
#         id='returns',
#         figure=fig2
#     ),
# ]),
# ])

# app.run_server(debug=True)