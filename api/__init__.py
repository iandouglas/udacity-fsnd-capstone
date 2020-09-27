import os

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
from config import config

db = SQLAlchemy()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    @app.route('/callback')
    def auth0_callback():
        return render_template('callback.html')

    @app.route('/')
    def home_page():
        auth0_url = os.getenv('AUTH0_URL')
        auth0_audience = os.getenv('AUTH0_AUDIENCE')
        auth0_client_id = os.getenv('AUTH0_CLIENTID')
        auth0_callbackurl = os.getenv('AUTH0_CALLBACKURL')
        auth0_callbackpath = os.getenv('AUTH0_CALLBACKPATH')

        login_link = f'https://{auth0_url}.auth0.com/authorize'\
            f'?audience={auth0_audience}'\
            f'&response_type=token'\
            f'&client_id={auth0_client_id}'\
            f'&redirect_uri={auth0_callbackurl}{auth0_callbackpath}'

        return render_template('index.html', link=login_link)

    return app
