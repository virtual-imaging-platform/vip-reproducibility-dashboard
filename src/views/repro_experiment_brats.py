import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, callback, Input, Output, dcc
from flask import request

from models.brats_utils import get_global_brats_experiment_data, download_brats_file


def layout():
    return html.Div(
        [
            html.H2('Visualize an experiment'),
            # Parameter menu
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4('File'),
                                    dcc.Dropdown(
                                        id='file-brats-exp',
                                        options=[
                                            {'label': 'All', 'value': 'All'}
                                        ],
                                        value='All',
                                        clearable=False,
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
                    html.Div(
                        # foreach group, show a boxplot
                        children=[
                            dcc.Graph(
                                id='general-chart-brats-exp',
                                config={"displayModeBar": False},
                            ),
                            dcc.Graph(
                                id='specific-file-chart-brats-exp',
                                config={"displayModeBar": False},
                                style={'display': 'none'},
                            ),
                        ],
                        className='card-body',
                    )
                ],
                className='card',
            ),
            html.Div(
                children=[
                    html.H3('Chart description'),
                    html.P(
                        children=[
                            'Description is loading...',
                        ],
                        id='description-exp-brats',
                    ),
                ],
            ),
            html.Div(
                html.Div(
                    children=[
                        html.H3("Visualize a file"),
                        # modal
                        dbc.Button(
                            "Open modal",
                            id="open-modal-brats-exp",
                            className="ml-auto",
                            color="primary",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(
                                    html.H3("Visualize a file")
                                ),
                                dbc.ModalBody(
                                    [
                                        html.P(
                                            children=[
                                                html.Span(
                                                    "Files for patient ",
                                                    className="font-weight-bold",
                                                ),
                                                html.Span(
                                                    "UPENN-GBM-00019",
                                                    id="patient-id-brats-exp",
                                                ),
                                                html.Span(
                                                    " on file type ",
                                                    className="font-weight-bold",
                                                ),
                                                html.Span(
                                                    "T1",
                                                    id="file-type-brats-exp",
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            children=[
                                                html.Div(

                                                ),
                                                html.Div(

                                                ),
                                            ],
                                            id='possible-files-brats-exp',
                                            className='card',
                                            style={'flexDirection': 'row'},
                                        ),
                                    ],
                                ),
                                dbc.ModalFooter(
                                    [
                                        dbc.Button(
                                            "Close", id="close-modal-brats-exp", className="ml-auto"
                                        ),
                                        dbc.Button(
                                            html.A(
                                                "Compare",
                                                id="compare-files-brats-exp",
                                                className="ml-auto",
                                                href="/compare_nii_11",
                                                style={'color': 'white', 'text-decoration': 'none'},
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                            id="modal-brats-exp",
                            size="xl",
                        ),
                    ],
                    className='card-body',
                ),
                className='card',
                id='modal-brats-exp-container',
                style={'display': 'none'},
            ),
        ]
    )


@callback(
    Output("modal-brats-exp", "is_open"),
    [Input("open-modal-brats-exp", "n_clicks"), Input("close-modal-brats-exp", "n_clicks")],
)
def toggle_modal(n1, n2):
    if n1 or n2:
        return not False
    return False


@callback(
    Output('general-chart-brats-exp', 'figure'),
    Output('file-brats-exp', 'options'),
    Output('description-exp-brats', 'children'),
    Input('general-chart-brats-exp', 'figure'),
    Input('file-brats-exp', 'value'),
)
def update_chart(_, file):
    exec_id = int(request.referrer.split('?')[1].split('=')[1])

    if file == 'All':
        experiment_data, files = get_global_brats_experiment_data(exec_id)
        description = 'Significant digits mean per step for each file. Significant digits are computed as with ' \
                      'https://raw.githubusercontent.com/gkpapers/2020AggregateMCA/master/code/utils.py. ' \
                      'The mean is computed for each step and each file.'
    else:
        experiment_data, files = get_global_brats_experiment_data(exec_id, file=file)
        description = f'Significant digits mean per step for file {file}. Significant digits are computed with ' \
                      f'https://raw.githubusercontent.com/gkpapers/2020AggregateMCA/master/code/utils.py. ' \
                      f'The mean is computed for each step.'


    files = [file for file in files]
    files.insert(0, 'All')

    figure = px.box(experiment_data, x="File", y="Mean_sigdigits", color="File", facet_col="Image",
                    title="Significant digits mean per step for each file", points="all",
                    category_orders={"Step": experiment_data['File'].unique().tolist(),
                                     "Image": experiment_data['Image'].unique().tolist()},
                    color_discrete_sequence=px.colors.qualitative.Plotly)
    figure.update_layout(
        yaxis_title="Significant digits mean",
    )
    return figure, [{'label': file, 'value': file} for file in files], description


@callback(
    Output('compare-files-brats-exp', 'href'),
    Input('file-1-brats-exp', 'value'),
    Input('file-2-brats-exp', 'value'),
    prevent_initial_call=True,
)
def update_compare_link(file_1, file_2):
    if file_1 is None or file_2 is None:
        return ""
    execution_number_1 = file_1.split('/-/')[0]
    execution_number_2 = file_2.split('/-/')[0]
    file = file_1.split('/-/')[1]
    patient_id = file_1.split('/-/')[2]
    experiment_id = int(request.referrer.split('?')[1].split('=')[1])
    md5_1 = download_brats_file(execution_number_1, file, patient_id, experiment_id)
    md5_2 = download_brats_file(execution_number_2, file, patient_id, experiment_id)
    return "/compare-nii-11?id1=" + md5_1 + "&id2=" + md5_2
