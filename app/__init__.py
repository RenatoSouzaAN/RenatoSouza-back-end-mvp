"""
__init__.py

This module sets up the Flask application, including configuration, database initialization,
authentication, and route registration.

It includes the following:
- Flask application factory (`create_app`) that configures the app.
- Logging configuration to output logs to stdout.
- Registration of database, migrations, CORS, and OAuth components.
- Error handlers for authentication errors and unhandled exceptions.
- A route to redirect the root URL to the API documentation.

Functions:
- create_app: Creates and configures the Flask application.
"""

import logging
import sys
import traceback

from flask import redirect, jsonify
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
# from cli import create_admin

from .extensions import db, migrate, oauth, info
from .auth import AuthError
from .routes import register_routes

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """ Create and configure an instance of the Flask application. """
    app = OpenAPI(__name__, info=info)
    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/dmarket.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    oauth.init_app(app)

    # app.cli.add_command(create_admin)

    oauth.register(
        "auth0",
        client_id=app.config['CLIENT_ID'],
        client_secret=app.config['CLIENT_SECRET'],
        client_kwargs={
            "scope": "openid profile email",
            "audience": app.config['API_AUDIENCE']
        },
        server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
    )

    security_scheme = {"bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "in": "header"}
        }
    app.security_schemes = security_scheme
    register_routes(app)

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        """ Handles authentication errors. """
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        """ Handles all unhandled exceptions. """
        if isinstance(e, HTTPException):
            return e

        logger.error("An unhandled exception occurred: %s", str(e))
        logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred"}), 500

    @app.get('/')
    def index():
        """Redirects to the API documentation."""
        return redirect('/openapi')

    return app
