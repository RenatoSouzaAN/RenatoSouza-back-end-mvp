"""
routes/product.py
This module defines the Product related API routes for the application.
It includes routes for:
- Product handling
Functions:
- get_product: Fetches details of a specific product.
- create_product: Creates a new product.
- update_product: Updates an existing product.
- delete_product: Deletes a product.
"""

import logging

from flask import jsonify, g, abort
from flask_openapi3 import APIBlueprint, Tag

from ..extensions import db
from ..auth import requires_auth
from ..models.product import Product
from ..schemas.product import ProductInput, ProductUpdate, ProductIdPath

product_bp = APIBlueprint('product', __name__)

product_tag = Tag(name='product', description='Product operations')

logger = logging.getLogger(__name__)

@product_bp.get('/products', tags=[product_tag],
    summary="List all products in the 'products' database.",
    description="Retrieve a list of all products in the database. "
                "Returns a message if no products are available.",     
    responses={
        200: {
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
            "description": "Returns a message if there are no Products "
                           "available in the 'products' database.",
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

    products_list = [product.to_dict() for product in products]
    return jsonify(products_list), 200


@product_bp.post('/products/create', tags=[product_tag],
    summary="Add a new product to the 'products' database, through 'Request Body'.",
    security=[{"bearerAuth": []}],
    description="Add a new product to the database by providing the "
                "required fields (name, price, and quantity).",
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
@requires_auth
def add_product(body: ProductInput):
    """Add a new product"""
    try:
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
            quantity=body.quantity,
            user_id=g.current_user.user_id
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully!'}), 202
    except Exception as e:
        logger.error("Error adding product: %s", str(e))
        db.session.rollback()
        return jsonify({'message': 'An error ocurred while adding the product.'}), 500
@product_bp.put('/products/<int:product_id>/update', tags=[product_tag],
    summary="Update an existing product's description, price, "
            "and quantity in the 'products' database, through 'Request Body'.",
    security=[{"bearerAuth": []}],
    description="Update a product's description, price, and/or quantity using "
                "the specified product ID. All three elements are optional.",
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
@requires_auth
def update_product(path: ProductIdPath, body: ProductUpdate):
    """Update a product"""
    product = db.session.get(Product, path.product_id)
    if not product:
        return jsonify({'message': 'Product not found.'}), 404

    if product.user_id != g.current_user.user_id and not g.current_user.is_admin:
        abort(403, description="You don't have permission to edit this product.")

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

@product_bp.delete('/products/<int:product_id>/delete', tags=[product_tag],
    summary="Delete a product",
    security=[{"bearerAuth": []}],
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
@requires_auth
def delete_product(path: ProductIdPath):
    """Delete a product"""
    product = db.session.get(Product, path.product_id)
    if not  product:
        return jsonify({'message': 'Product not found'}), 404

    if product.user_id != g.current_user.user_id and not g.current_user.is_admin:
        abort(403, description="You don't have permission to delete this product.")

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully.'}), 200
