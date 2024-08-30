"""
models.py

This module defines the SQLAlchemy models for the application,
including the `Product` and `User` models.

Classes:
- Product: Represents a product in the inventory with fields for name,
  description, price, quantity, and user relationship.
- User: Represents a user with fields for ID, email, name, and admin status.

Each class includes methods for initialization, conversion to dictionary (for `User`),
and string representation.
"""

from dataclasses import dataclass, field
from .extensions import db

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

class User(db.Model):
    """
    Represents a user in the database.

    Attributes:
        user_id (str): The unique identifier of the user.
        email (str): The email address of the user.
        name (str): The name of the user.
        is_admin (bool): Whether the user has admin privileges.
    """
    __tablename__ = 'users'
    user_id = db.Column(db.String(64), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, email, name, is_admin=False):
        """
        Initializes a new User instance.

        Args:
            user_id (str): The unique identifier of the user.
            email (str): The email address of the user.
            name (str): The name of the user.
            is_admin (bool): Whether the user has admin privileges. Defaults to False.
        """
        self.user_id = user_id
        self.email = email
        self.name = name
        self.is_admin = is_admin

    def to_dict(self):
        """
        Converts the User instance to a dictionary.

        Returns:
            dict: A dictionary representation of the user.
        """
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'is_admin': self.is_admin,
        }

    def __repr__(self):
        return f'<User {self.email}>'

    def set_admin(self, is_admin=True):
        """
        Sets the admin status of the user.

        Args:
            is_admin (bool): Whether to set the user as an admin. Defaults to True.
        """
        self.is_admin = is_admin
