""" 
outes/__init__.py

This module initializes the routes package and provides a function to register 
all API blueprints with the Flask application.

The routes define the API endpoints of the application, handling HTTP requests 
and responses.

Blueprints:
    auth_bp: Handles authentication-related routes.
    product_bp: Handles product-related routes.

Functions:
    register_routes(app): Registers all blueprints with the given Flask app.

Usage:
    from app.routes import register_routes
    register_routes(app)
"""

from .auth import auth_bp
from .product import product_bp

def register_routes(app):
    """
    Register all route blueprints with the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """
    app.register_api(auth_bp)
    app.register_api(product_bp)
