import os
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import HTTPException
from api.auth.auth import requires_auth, AuthError
from config import config

db = SQLAlchemy()


class ExtendedAPI(Api):
    """
    credit to https://stackoverflow.com/a/57921890
    adapted the code for the cafe scenario
    This class overrides 'handle_error' method of 'Api' class in Flask-RESTful,
    to extend global exception handing functionality
    """
    def handle_error(self, err):  # pragma: no cover
        """
        prevents writing unnecessary try/except block thoughout the application
        """
        # log every exception raised in the application
        print('API handle_error()', err, err.__class__)

        # catch our custom AuthError
        if isinstance(err, AuthError):
            return jsonify({
                'success': False,
                'error': err.error,
                'code': getattr(err, 'code'),
                'description': getattr(err, 'description'),
            }), err.status_code

        # catch other werkzeug http errors
        if isinstance(err, HTTPException):
            original = getattr(err, "original_exception", None)
            return jsonify({
                'success': False,
                'error': err.code,
                "message": getattr(err.error, 'message')
                }), err.code

        # if 'message' attribute isn't set, assume it's a core Python exception
        if not getattr(err, 'message', None):
            original = getattr(err, "original_exception", None)
            return jsonify({
                'message': 'Server has encountered an unknown error'
                }), 500

        # Handle application-specific custom exceptions
        return jsonify(**err.kwargs), err.http_status_code


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    api = ExtendedAPI(app)

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

    from api.resources.forecast import ForecastResource
    from api.resources.roadtrips import RoadtripsResource, RoadtripResource

    api.add_resource(ForecastResource, '/api/forecast')
    api.add_resource(RoadtripResource, '/api/roadtrips/<roadtrip_id>')
    api.add_resource(RoadtripsResource, '/api/roadtrips')

    return app
