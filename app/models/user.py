"""
models.py

This module defines the SQLAlchemy `User` model for the application.

Classes:
- User: Represents a user with fields for ID (user_id), email, name, and admin status.

In this class is included methods for initialization, conversion to dictionary,
and string representation.
"""

from ..extensions import db

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