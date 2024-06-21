from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/dmarket.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    from .routes import register_routes
    register_routes(app, db)

    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "DMarket API Documentation"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route('/')
    def index():
        """Redireciona para a tela de documentação '/swagger'.
        """
        return redirect('/swagger')
    
    return app