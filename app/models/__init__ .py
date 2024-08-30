"""
models/__init__.py

This module initializes the models package and imports all model classes.

The models represent the data structures used in the application and their 
relationships. They are used by SQLAlchemy to interact with the database.

Classes:
    Product: Represents a product in the inventory.
    User: Represents a user of the application.

Usage:
    from app.models import Product, User
"""

from .product import Product
from .user import User
