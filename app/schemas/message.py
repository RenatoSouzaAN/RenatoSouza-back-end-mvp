"""
schemas/message.py

This module defines the Pydantic models (schemas) for the application,
which are used for data validation and serialization.

Classes:
- MessageResponse: Schema for a message response.
"""

from pydantic import BaseModel, Field

class MessageResponse(BaseModel):
    """
    Schema for a message response.
    """
    message: str = Field(..., description="Message response")
