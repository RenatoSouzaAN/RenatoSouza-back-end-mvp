from flask import Flask, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_openapi3 import OpenAPI, Info
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from .auth import AuthError

db = SQLAlchemy()
oauth = OAuth()
info = Info(title="DMarket API", version="2.0.0")

def create_app():
    app = OpenAPI(__name__, info=info)
    
    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/dmarket.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    oauth.init_app(app)

    oauth.register(
        "auth0",
        client_id=app.config['CLIENT_ID'],
        client_secret=app.config['CLIENT_SECRET'],
        client_kwargs={
            "scope": "openid profile email"
        },
        server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
    )

    # Define security scheme
    security_scheme = {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}
    app.security_schemes = security_scheme

    from .routes import api
    app.register_api(api)

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    @app.get('/')
    def index():
        """Redirects to the API documentation."""
        return redirect('/openapi')

    return app