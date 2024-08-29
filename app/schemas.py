"""
schemas.py

This module defines the Pydantic models (schemas) for the application,
which are used for data validation and serialization.

Classes:
- GetProduct: Schema for returning product details.
- ProductInput: Schema for creating a new product.
- ProductUpdate: Schema for updating an existing product.
- ProductIdPath: Schema for specifying a product ID in the path.
- MessageResponse: Schema for a message response.
- AdminSetBody: Schema for setting a user as an admin by email.
"""

from pydantic import BaseModel, Field

class GetProduct(BaseModel):
    """
    Schema for returning product details.
    """
    id: int = Field(...,
                        description="Product ID")
    name: str = Field(...,
                        description="Product name")
    description: str | None = Field(description="Product description")
    price: float = Field(...,
                        description="Product price")
    quantity: int = Field(...,
                        description="Product quantity")

class ProductInput(BaseModel):
    """
    Schema for creating a new product.
    """
    name: str = Field(...,
                        description="Product name (required)")
    description: str | None = Field(description="Product description (optional)")
    price: float = Field(..., gt=0,
                        description="Product price (required, must be greater than 0)")
    quantity: int = Field(..., gt=0,
                        description="Product quantity (required, must be greater than 0)")

class ProductUpdate(BaseModel):
    """
    Schema for updating an existing product.
    """
    description: str | None = Field(description="Product description (optional)")
    price: float | None = Field(gt=0,
                        description="Product price (optional, must be greater than 0)")
    quantity: int | None = Field(gt=0,
                        description="Product quantity (optional, must be greater than 0)")

class ProductIdPath(BaseModel):
    """
    Schema for specifying a product ID in the path.
    """
    product_id: int = Field(..., description="Product ID (required)")

class MessageResponse(BaseModel):
    """
    Schema for a message response.
    """
    message: str = Field(..., description="Message response")

class AdminSetBody(BaseModel):
    """
    Schema for setting a user as an admin by email.
    """
    email: str = Field(..., description="Email of the user to be set as admin")
