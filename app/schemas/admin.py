"""
schemas/admin.py

This module defines the Pydantic models (schemas) for the application,
which are used for data validation and serialization.

Classes:
- AdminSetBody: Schema for setting a user as an admin by email.
- UserIdPath: Schema for specifying a user ID in the path.
"""

from pydantic import BaseModel, Field

class AdminSetBody(BaseModel):
    """
    Schema for setting a user as an admin by email.
    """
    email: str = Field(..., description="Email of the user to be set as admin")

class UserIdPath(BaseModel):
    """ 
    Schema for specifying a user ID in the path.
    """
    user_id: str = Field(..., description="The ID of the user to delete")
