from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_openapi3 import OpenAPI, Info
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
info = Info(title="DMarket API", version="2.0.0")