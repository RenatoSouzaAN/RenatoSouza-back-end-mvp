from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel

from .models import Product
from .schemas import ProductInput, GetProduct, ProductUpdate, MessageResponse
from . import db

api = APIBlueprint('api', __name__, url_prefix='/api')

product_tag = Tag(name='product', description='Product operations')

class ProductIdPath(BaseModel):
    product_id: int

@api.get('/products', tags=[product_tag], summary="List all products in the 'products' database.", 
    description="Retrieve a list of all products in the database. Returns a message if no products are available.",
    responses={
        "200": {
            "description": "Returns a list of Products available in the 'products' database.",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "description": "Product ID"
                            },
                            "name": {
                                "type": "string",
                                "description": "Product name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Product description"
                            },
                            "price": {
                                "type": "number",
                                "description": "Product price"
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "Product quantity"
                            }
                        }
                    }
                }
            }
        },
        201: {
            "description": "Returns a message if there are no Products available in the 'products' database.", 
            "content": {
                "application/json": {
                    "examples": {
                        "emptyDatabase": {
                            "summary": "The 'products' database is empty.",
                            "value": {
                                "message": "The products database is empty."
                            }
                        }
                    }
                }
            }
        },
    }
)
def get_products():
    """Get all products"""
    products = Product.query.all()
    if not products:
        return jsonify({'message': 'The Products database is empty'}), 201
    
    products_list = [
        GetProduct(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity
        ).model_dump()
        for product in products
    ]
    return jsonify(products_list), 200

@api.post('/products/create', tags=[product_tag], summary="Add a new product to the 'products' database, through 'Request Body'.",
    description="Add a new product to the database by providing the required fields (name, price, and quantity).", 
    responses={
        202: {"description": "Product added successfully to the 'products' database."},
        400: {
            "description": "Invalid input", 
            "content": {
                "application/json": {
                    "examples": {
                        "MissingName": {
                            "summary": "Missing name",
                            "value": {
                                "message": "Name is required"
                            }
                        },
                        "MissingPrice": {
                            "summary": "Missing price",
                            "value": {
                                "message": "Price is required"
                            }
                        },
                        "MissingQuantity": {
                            "summary": "Missing quantity",
                            "value": {
                                "message": "Quantity is required"
                            }
                        },
                        "InvalidPrice": {
                            "summary": "Invalid price",
                            "value": {
                                "message": "Price must be a number"
                            }
                        },
                        "InvalidQuantity": {
                            "summary": "Invalid quantity",
                            "value": {
                                "message": "Quantity must be an integer"
                            }
                        },
                        "PriceTooLow": {
                            "summary": "Price too low",
                            "value": {
                                "message": "Price must be higher than 0"
                            }
                        },
                        "QuantityTooLow": {
                            "summary": "Quantity too low",
                            "value": {
                                "message": "Quantity must be higher than 0"
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "examples": {
                        "UnprocessableEntity": {
                            "summary": "Unprocessable Entity",
                            "value": {
                                "message": "This entity can't be processed."
                            }
                        }
                    }
                }
            }
        }
    }
)
def add_product(body: ProductInput):
    """Add a new product"""
    if not body.name:
        return jsonify({'message': 'Name is required'}), 400
    
    if body.price < 1:
        return jsonify({'message': 'Price must be higher than 0.'}), 400
    
    if body.quantity < 1:
        return jsonify({'message': 'Quantity must be higher than 0.'}), 400
   
    new_product = Product(
        name=body.name,
        description=body.description,
        price=body.price,
        quantity=body.quantity
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully!'}), 202

@api.put('/products/<int:product_id>/update', tags=[product_tag], summary="Update an existing product's description, price, and quantity in the 'products' database, through 'Request Body'.",
    description="Update a product's description, price, and/or quantity using the specified product ID. All three elements are optional.",
    responses={
        203: {
            "description": "Product updated successfully in the 'products' database.", 
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "Update successful",
                            "value": {
                                "message": "Product updated successfully!"
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid input", 
            "content": {
                "application/json": {
                    "examples": {
                        "InvalidPrice":{
                            "summary": "Invalid price",
                            "value": {
                                "message": "Price must be a number.",
                            }
                        },
                        "InvalidQuantity":{
                            "summary": "Invalid quantity",
                            "value": {
                                "message": "Quantity must be a number.",
                            }
                        },
                        "PriceTooLow":{
                            "summary": "Price too low",
                            "value": {
                                "message": "Price must be higher than 0.",
                            }
                        },
                        "QuantityTooLow":{
                            "summary": "Quantity too low",
                            "value": {
                                "message": "Quantity must be higher than 0.",
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "Product not found in the 'products' database.", 
            "content": {
                "application/json": {
                    "examples": {
                        "NotFound": {
                            "summary": "Product not found",
                            "value": {
                                "message": "Product not found"
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "examples": {
                        "UnprocessableEntity": {
                            "summary": "Unprocessable Entity",
                            "value": {
                                "message": "This entity can't be processed."
                            }
                        }
                    }
                }
            }
        }
    }
)
def update_product(path: ProductIdPath, body: ProductUpdate):
    """Update a product"""
    product = db.session.get(Product, path.product_id)
    if not product:
        return jsonify({'message': 'Product not found.'}), 404
   
    if body.description:
        product.description = body.description

    if body.price is not None:
        if body.price < 1:
            return jsonify({'message': 'Price must be higher than 0.'}), 400
        
        product.price = body.price

    if body.quantity is not None:
        if body.quantity < 1:
            return jsonify({'message': 'Quantity must be higher than 0.'}), 400
        
        product.quantity = body.quantity
       
    db.session.commit()
    return jsonify({'message': 'Product updated successfully.'}), 203

@api.delete('/products/<int:product_id>/delete', tags=[product_tag], summary="Delete a product",
    description="Delete a product from the 'products' database using the specified product ID.",    
    responses={
        200: {
            "description": "Product deleted successfully from the 'products' database.", 
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "Product deleted successfully.",
                            "value": {
                                "message": "Product deleted successfully."
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid input", 
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "Invalid input provided.",
                            "value": {
                                "message": "Input provided is invalid, please input a valid ID."
                            }
                        }
                    }
                }
            }
        },
        404: {"description": "Product not found", 
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "Product not found.",
                            "value": {
                                "message": "Product with ID provided not found."
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "examples": {
                        "UnprocessableEntity": {
                            "summary": "Unprocessable Entity",
                            "value": {
                                "message": "This entity can't be processed."
                            }
                        }
                    }
                }
            }
        }
    }
)
def delete_product(path: ProductIdPath):
    """Delete a product"""
    product = db.session.get(Product, path.product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully.'}), 200
    return jsonify({'message': 'Product not found'}), 404