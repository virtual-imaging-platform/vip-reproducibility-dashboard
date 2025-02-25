"""
View for the compare xy (many to many files) page for cquest.
"""
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, callback, Input, Output, dcc
from flask import request

from models.spectro_utils import (get_same_files_in_folders, normalize_lcmodel, read_folder_lcmodel,
                                  preprocess_lcmodel_data_compare,
                                  read_file_in_folder_lcmodel, get_files_in_folder, read_folders_lcmodel,
                                  read_file_in_folders_lcmodel)
from models.reproduce import parse_url


def layout():
    """Return the layout for the compare xy page for cquest."""
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2('Compare LCModel files'),
            dbc.Input(id='data-id1', type='hidden', value=''),
            dbc.Input(id='data-id2', type='hidden', value=''),
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('File'),
                                    dcc.Dropdown(
                                        id='file-selected-compare-lcmodel-x',
                                        options=[
                                        ],
                                        value='',
                                        clearable=False,
                                    ),
                                    dcc.Checklist(
                                        id='aggregate-data-compare-lcmodel-x',
                                        options=[
                                            {'label': 'Aggregate data', 'value': 'aggregate'},
                                        ],
                                        value=[],
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Normalization'),
                                    dcc.RadioItems(
                                        id='normalization-compare-x-lcmodel',
                                        options=[
                                            {'label': 'No', 'value': 'No'},
                                            {'label': 'Yes', 'value': 'Yes'},
                                        ],
                                        value='No',
                                        labelStyle={'display': 'block'},
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Graph type'),
                                    dcc.RadioItems(
                                        id='graph-type-compare-x-lcmodel',
                                        options=[
                                            {'label': 'Box', 'value': 'Box'},
                                            {'label': 'Violin', 'value': 'Violin'},
                                            {'label': 'scatter', 'value': 'scatter'},
                                        ],
                                        value='Box',
                                        labelStyle={'display': 'block'},
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                            dbc.Col(
                                children=[
                                    html.H4('Low cut'),
                                    dcc.RadioItems(
                                        id='low-cut-compare-x-lcmodel',
                                        options=[
                                            {'label': 'No', 'value': False},
                                            {'label': 'Yes', 'value': True},
                                        ],
                                        value=True,
                                        labelStyle={'display': 'block'},
                                    ),
                                ],
                                width=3,
                                className='card-body',
                            ),
                        ],
                        className='card',
                        style={'flexDirection': 'row'},
                    ),
                ]
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id='x-chart-compare-lcmodel',
                        config={"displayModeBar": False},
                    ),
                ], 
                className='card',
            ),
        ]
    )


@callback(
    Output('file-selected-compare-lcmodel-x', 'options'),
    Output('file-selected-compare-lcmodel-x', 'value', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call='initial_duplicate',
)
def bind_selects(_):
    """Bind the charts to the data"""
    if len(request.referrer.split('?')) <= 1:
        return [], []
    id = parse_url(request.referrer)[0]
    files = get_same_files_in_folders(id, 'table')
    return [{'label': file, 'value': file} for file in files], files[0]


@callback(
    Output('x-chart-compare-lcmodel', 'figure'),
    Output('file-selected-compare-lcmodel-x', 'value', allow_duplicate=True),
    Input('file-selected-compare-lcmodel-x', 'value'),
    Input('aggregate-data-compare-lcmodel-x', 'value'),
    Input('normalization-compare-x-lcmodel', 'value'),
    Input('graph-type-compare-x-lcmodel', 'value'),
    Input('low-cut-compare-x-lcmodel', 'value'),
    prevent_initial_call=True,
)
def update_chart(file, aggregate, normalization, graph_type, low_cut):
    """Bind the charts to the data"""
    id = parse_url(request.referrer)[0]
    if aggregate:
        data = read_folders_lcmodel(id)
    else:
        data = read_file_in_folders_lcmodel(id, file)
    graph_type_list = {
        'Box': px.box,
        'Violin': px.violin,
        'scatter': px.scatter
    }
    if low_cut:
        data = data[data['Rate_Cr'] > 5]
    if data.empty:
        return {}, file
    fig = graph_type_list[graph_type](
        x=data['Metabolite'],
        y=data['Rate_Cr'],
        title='Metabolite rates',
        labels={'x': 'Metabolite', 'y': 'Rate'},
        data_frame=data,
        color='Folder',
    )
    return fig, file


def mean_square_error(data1, data2):
    """Compute the mean square error between two dataframes"""
    return ((data1 - data2) ** 2).mean().mean()
