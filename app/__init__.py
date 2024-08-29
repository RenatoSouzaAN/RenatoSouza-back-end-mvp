import logging
import sys

from flask import redirect, jsonify
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from .extensions import db, migrate, oauth, info
from .auth import AuthError
from cli import create_admin
from werkzeug.exceptions import HTTPException
import traceback

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    app = OpenAPI(__name__, info=info)
    
    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/dmarket.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    oauth.init_app(app)

    app.cli.add_command(create_admin)

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

    security_scheme = {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT", "in": "header"}}
    app.security_schemes = security_scheme

    from .routes import api
    app.register_api(api)

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
        
        logger.error(f"An unhandled exception occurred: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred"}), 500

    @app.get('/')
    def index():
        """Redirects to the API documentation."""
        return redirect('/openapi')

    return app