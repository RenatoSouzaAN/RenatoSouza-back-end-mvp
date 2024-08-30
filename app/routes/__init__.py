from .auth import auth_bp
from .product import product_bp

def register_routes(app):
    app.register_api(auth_bp)
    app.register_api(product_bp)