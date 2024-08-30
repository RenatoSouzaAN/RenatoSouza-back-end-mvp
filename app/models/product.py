"""
models.py

This module defines the SQLAlchemy `Product` model for the application.

Classes:
- Product: Represents a product in the inventory with fields for name,
  description, price, quantity, and user relationship.

In this class is included methods for initialization, conversion to dictionary,
and string representation.
"""

from dataclasses import dataclass, field
from ..extensions import db

@dataclass
class Product(db.Model):
    """
    Represents a product in the database.

    Attributes:
        id (int): The unique identifier of the product.
        name (str): The name of the product.
        description (str): The description of the product.
        price (float): The price of the product.
        quantity (int): The quantity available of the product.
        user_id (str): The ID of the user who owns the product.
        user (User): The user associated with the product.
    """
    __tablename__ = 'products'

    id: int = field(init=False)
    name: str
    description: str
    price: float
    quantity: int
    user_id: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, nullable=False)
    description = db.Column(db.String(120))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), nullable=False, index=True)

    user = db.relationship('User', backref=db.backref('products', lazy=True))

    def __post_init__(self):
        if self.id is None:
            self.id = None

    def to_dict(self):
        """
        Converts the Product instance to a dictionary.

        Returns:
            dict: A dictionary representation of the product.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'quantity': self.quantity,
            'user_id': self.user_id
        }

    def __repr__(self):
        return f'<Product {self.name}>'