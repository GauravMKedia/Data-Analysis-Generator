#!/usr/bin/env python
# coding: utf-8

import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
import seaborn as sns
import warnings
import math
from sklearn.impute import SimpleImputer
import datetime as dt
from itertools import combinations
from collections import Counter
import dash
import jupyter_dash
import plotly.io as pio
import pickle
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
warnings.filterwarnings("ignore")
plt.rcParams["figure.figsize"] = (15,6)
plt.rcParams['figure.dpi'] = 70


def is_array(obj):
    return isinstance(obj, list)

# load the dictionary from the saved file
with open('assets/Figure.pickle', 'rb') as f:
    main_data_dict = pickle.load(f)

# print the dictionary to verify it was loaded correctly
# print(main_data_dict)

external_stylesheets = ['assets/style.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

# Create the layout
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='dropdown1',
            options=[{'label': k, 'value': k} for k in main_data_dict.keys()],
            value=list(main_data_dict.keys())[0],
            className='dropdown1'
        ),
        dcc.Dropdown(id='dropdown2', className='dropdown2'),
        dcc.Dropdown(id='dropdown3', multi=True, className='dropdown3'),
        html.Button('DataFrames', id='toggle-button', n_clicks=0, className='button'),
        html.Div(id='output-container', className='output-container')
    ], className='container'),
    html.Div(className='media-container', children=[html.P('Please Use Laptop')]),
], className='outer-container')

# Create the callback functions
@app.callback(
    dash.dependencies.Output('dropdown2', 'options'),
    [dash.dependencies.Input('dropdown1', 'value')]
)
def update_dropdown2_options(selected_key):
    # print(f"Key:{selected_key}, Subkey1:{type(main_data_dict[selected_key])}")
    sub_dict = main_data_dict[selected_key]
    return [{'label': k, 'value': k} for k in sub_dict.keys()]

@app.callback(
    dash.dependencies.Output('dropdown2', 'value'),
    [dash.dependencies.Input('dropdown2', 'options')]
)
def update_dropdown2_value(options):
    # print(f"OPTIONS is : {options}\n")
    return options[0]['value']

@app.callback(
    dash.dependencies.Output('dropdown3', 'options'),
    [dash.dependencies.Input('dropdown1', 'value'),
     dash.dependencies.Input('dropdown2', 'value')]
)
def update_dropdown3_options(selected_key, selected_subkey):
    # print(f"HKey:{selected_key}, HSubkey1:{selected_subkey}, HSubkey2:{type(main_data_dict[selected_key][selected_subkey])}")
    figure_dict = main_data_dict[selected_key][selected_subkey]
    return [{'label': k, 'value': k} for k in figure_dict.keys()]

@app.callback(
    
    dash.dependencies.Output('dropdown3', 'value'), 
    [dash.dependencies.Input('dropdown3', 'options')]
)
def update_dropdown3_value(options):
    # print(f"Value is : {options[0]['value']}")
    return options[0]['value']

@app.callback(
    dash.dependencies.Output('output-container', 'children'),
    [dash.dependencies.Input('dropdown1', 'value'),
     dash.dependencies.Input('dropdown2', 'value'),
     dash.dependencies.Input('dropdown3', 'value'),
     dash.dependencies.Input('toggle-button', 'n_clicks')]
)


def display_data(selected_key, selected_subkey, keys, n_clicks):
    if not keys:
        return None
    if isinstance(keys, str):
        keys = [keys]

    # print(f"Key:{selected_key}, Subkey1:{selected_subkey}")    
    # for key in keys:
    #     print(f"Selected Multi Key is :{key}")
    
    temp = main_data_dict[selected_key][selected_subkey]
    figure_dict=[temp[k] for k in keys]
    components = []
    i=1
    for fig in figure_dict:
        if not is_array(fig):
            components.append(html.Div([
                html.H3(f"Dataframe {i}:"),
                html.Div([
                    dcc.Markdown(f"```{fig}```")
                ])
            ]))
            i+=1
        else:
            if n_clicks % 2 == 1:
                for df in fig[1:]:
                    components.append(html.Div([
                        html.H3(f"Dataframe {i}:"),
                        html.Div([
                            dcc.Markdown(f"```{df}```")
                        ])
                    ]))
                    i+=1
            else:
                components.append(dcc.Graph(figure=fig[0]))
                # components=components
    return components


    

if __name__ == '__main__':
    app.run_server(debug=True)
