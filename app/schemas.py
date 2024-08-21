from pydantic import BaseModel, Field

class GetProduct(BaseModel):
    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: str | None = Field(description="Product description")
    price: float = Field(..., description="Product price")
    quantity: int = Field(..., description="Product quantity")

class ProductInput(BaseModel):
    name: str = Field(..., description="Product name (required)")
    description: str | None = Field(description="Product description (optional)")
    price: float = Field(..., gt=0, description="Product price (required, must be greater than 0)")
    quantity: int = Field(..., gt=0, description="Product quantity (required, must be greater than 0)")

class ProductUpdate(BaseModel):
    description: str | None = Field(description="Product description (optional)")
    price: float | None = Field(gt=0, description="Product price (optional, must be greater than 0)")
    quantity: int | None = Field(gt=0, description="Product quantity (optional, must be greater than 0)")

class ProductIdPath(BaseModel):
    product_id: int = Field(..., description="Product ID (required)")

class MessageResponse(BaseModel):
    message: str = Field(..., description="Message response")