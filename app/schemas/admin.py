"""
schemas/message.py

This module defines the Pydantic models (schemas) for the application,
which are used for data validation and serialization.

Classes:
- AdminSetBody: Schema for setting a user as an admin by email.
"""

from pydantic import BaseModel, Field

class AdminSetBody(BaseModel):
    """
    Schema for setting a user as an admin by email.
    """
    email: str = Field(..., description="Email of the user to be set as admin")
