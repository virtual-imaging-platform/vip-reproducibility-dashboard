# -----------------------------------------------------------------------------
# Description : Main application file. It defines the layout of the application
# Author      : Hippolyte Blot. <hippolyte.blot@creatis.insa-lyon.fr>
# Created on  : 2023-10-27
# -----------------------------------------------------------------------------
"""
Main application file. It defines the layout of the application
"""
import os
import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_restful import Api
import ssl

# local imports
from utils.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK, SSL_CERT_CHAIN, SSL_SERVER_KEY
from components import navbar, footer
from api.girder_scanner import GirderScanner


def create_app():
    """The create_app function is used to create the Dash app. It is used to create the app in the main.py file."""
    server = Flask(__name__)
    local_app = dash.Dash(
        __name__,
        server=server,
        use_pages=True,  # turn on Dash pages
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.FONT_AWESOME
        ],  # fetch the proper css items we want
        meta_tags=[
            {  # check if device is a mobile device. This is a must if you do any mobile styling
                'name': 'viewport',
                'content': 'width=device-width, initial-scale=1'
            }
        ],
        suppress_callback_exceptions=True,
        title='Reproducibility Dashboard'
    )

    server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))

    def serve_layout():
        """Define the layout of the application"""
        return html.Div(
            [
                navbar,
                dbc.Container(
                    dash.page_container,
                    class_name='my-2'
                ),
                footer
            ]
        )

    local_app.layout = serve_layout  # set the layout to the serve_layout function

    return local_app


context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain(certfile=SSL_CERT_CHAIN, keyfile=SSL_SERVER_KEY)
app = create_app()
api = Api(app.server)
api.add_resource(GirderScanner, '/api/girder_scanner')
app.run_server(
    host=APP_HOST,
    port=APP_PORT,
    debug=APP_DEBUG,
    dev_tools_props_check=DEV_TOOLS_PROPS_CHECK,
    ssl_context=context
)
