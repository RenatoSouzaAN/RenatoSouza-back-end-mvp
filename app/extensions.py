"""
extensions.py

This module contains the database, migrations, and OAuth components for the application.

Classes:
- db: SQLAlchemy database object.
- migrate: Flask-Migrate object.
- oauth: Flask-OpenAPI3 OAuth object.
- info: Flask-OpenAPI3 Info object.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_openapi3 import Info
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
info = Info(title="DMarket API", version="2.0.0")
