"""
schemas/__init__.py

This module initializes the schemas package and imports all Pydantic model classes.

The schemas define the structure for request/response data validation and 
serialization using Pydantic models.

Classes:
    GetProduct: Schema for returning product details.
    ProductInput: Schema for creating a new product.
    ProductUpdate: Schema for updating an existing product.
    ProductIdPath: Schema for specifying a product ID in the path.
    MessageResponse: Schema for a message response.
    AdminSetBody: Schema for setting a user as an admin by email.

Usage:
    from app.schemas import GetProduct, ProductInput, ProductUpdate, ProductIdPath, MessageResponse, AdminSetBody
"""

from .product import GetProduct, ProductInput, ProductUpdate, ProductIdPath
from .message import MessageResponse
from .admin import AdminSetBody
