"""
Compare two quest2 files of cquest
"""
import pandas as pd
from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import request

from models.spectro_utils import read_cquest_file, normalize_cquest, preprocess_cquest_data_compare, read_lcmodel_file, \
    preprocess_lcmodel_data_compare
from models.reproduce import parse_url


def layout():
    """Return the layout for the compare quest2 files page."""
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.H2('Compare LDModel files'),
            dbc.Input(id='data-id1', type='hidden', value=''),
            dbc.Input(id='data-id2', type='hidden', value=''),

            html.Div(
                children=[
                    dcc.Graph(
                        id='11-chart-compare-lcmodel',
                        config={"displayModeBar": False},
                    ),
                ],
                className='card',
            ),
        ]
    )


@callback(
    Output('11-chart-compare-lcmodel', 'figure'),
    Input('url', 'pathname'),
)
def bind_charts(_):
    """Bind the charts to the data"""
    if len(request.referrer.split('?')) < 2:
        return {}
    id1, id2 = parse_url(request.referrer)
    data1 = read_lcmodel_file(id1)
    data2 = read_lcmodel_file(id2)
    # delete metabolites water1, water2, water3
    data1, data2 = preprocess_lcmodel_data_compare(data1, data2)

    data = pd.concat([data1, data2])

    fig1 = px.scatter(
        x=data['Metabolite'],
        y=data['Rate_Cr'],
        title='Comparison of metabolites',
        labels={
            'x': 'Metabolite',
            'y': 'Rate_Cr',
            'color': 'File',
        },
        color=data['File'],
    )
    return fig1
