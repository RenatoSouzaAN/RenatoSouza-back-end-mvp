from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_openapi3 import OpenAPI, Info
from flask_cors import CORS

db = SQLAlchemy()

info = Info(title="DMarket API", version="2.0.0")

def create_app():
    app = OpenAPI(__name__, info=info)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/dmarket.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate = Migrate(app, db)

    CORS(app)

    from .routes import api
    app.register_api(api)

    @app.get('/')
    def index():
        """Redirects to the API documentation."""
        return redirect('/openapi')

    return app