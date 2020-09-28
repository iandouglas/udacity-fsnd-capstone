import os

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify

from api.auth.auth import requires_auth, AuthError
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

    @app.errorhandler(AuthError)
    @app.errorhandler(401)
    def not_authenticated(error):
        """
        error handler for 401
        """
        return jsonify({
            "success": False,
            "error": 401,
            "message": "unauthorized"
        }), 401

    @app.errorhandler(403)
    def not_authorized(error):
        """
        error handler for 403
        """
        return jsonify({
            "success": False,
            "error": 403,
            "message": "forbidden"
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        """
        error handler for 404
        """
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.route('/auth-required')
    @requires_auth('create:roadtrips')
    def auth_required(payload):
        return jsonify({
            "success": True,
            "message": "authorized"
        }), 200

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
