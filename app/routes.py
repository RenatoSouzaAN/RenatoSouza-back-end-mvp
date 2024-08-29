from flask import jsonify, redirect, request, url_for, session, current_app, g, abort
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel
from urllib.parse import urlencode

from .models import Product, User
from .schemas import ProductInput, GetProduct, ProductUpdate, ProductIdPath, AdminSetBody
from .extensions import db, oauth
from .auth import requires_auth, requires_admin,  get_or_create_user
from config import Config

import logging

api = APIBlueprint('api', __name__)

product_tag = Tag(name='product', description='Product operations')
admin_tag = Tag(name='admin', description='Admin operations')

logger = logging.getLogger(__name__)

@api.get('/products', tags=[product_tag], summary="List all products in the 'products' database.", 
    description="Retrieve a list of all products in the database. Returns a message if no products are available.",
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
    security=[{"bearerAuth": []}],
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
@requires_auth
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
        quantity=body.quantity,
        user_id=g.current_user.id
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully!'}), 202

@api.put('/products/<int:product_id>/update', tags=[product_tag], summary="Update an existing product's description, price, and quantity in the 'products' database, through 'Request Body'.",
    security=[{"bearerAuth": []}],
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
@requires_auth
def update_product(path: ProductIdPath, body: ProductUpdate):
    """Update a product"""
    product = db.session.get(Product, path.product_id)
    if not product:
        return jsonify({'message': 'Product not found.'}), 404
   
    if product.user_id != g.current_user.id and not g.current_user.is_admin:
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

@api.delete('/products/<int:product_id>/delete', tags=[product_tag], summary="Delete a product",
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
    
    if product.user_id != g.current_user.id and not g.current_user.is_admin:
        abort(403, description="You don't have permission to delete this product.")

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully.'}), 200

@api.post('/admin/set', tags=[admin_tag], summary="Set a user as admin", 
    security=[{"bearerAuth": []}],
    description="Set a user as an admin. Only current admins can set new ones.",
    responses={
        200: {"description": "User set as admin successfully"},
        403: {"description": "Only existing admins can set new admins"},
        404: {"description": "User not found"},
    })
@requires_auth
@requires_admin
def set_admin(body: AdminSetBody):
    """Set a user as admin"""    
    user = User.query.filter_by(email=body.email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.is_admin = True
    db.session.commit()
    return jsonify({'message': 'User set as admin successfully'}), 200

@api.get('/admin/check', security=[{"bearerAuth": []}])
@requires_auth
def check_admin():
    return jsonify({'is_admin': g.current_user.is_admin}), 200

@api.get('/login', summary="Initiate login process",
    description="Redirects the user to the Auth0 login page."
)
def login():
    """ Initiate login process """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("api.callback", _external=True),
        audience=Config.API_AUDIENCE,
        scope="openid profile email"
    )

@api.get('/callback', summary="Auth0 callback",
    description="Handles the callback from Auth0 after user authentication."
)
def callback():
    """ Handles the callback from Auth0 after user authentication. """
    try:
        token = oauth.auth0.authorize_access_token()
        
        userinfo_endpoint = f"https://{Config.AUTH0_DOMAIN}/userinfo"
        resp = oauth.auth0.get(userinfo_endpoint)
        userinfo = resp.json()

        user = get_or_create_user(userinfo)

        session['user'] = {
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'access_token': token['access_token']
        }
        return redirect("/")
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        return jsonify({"error": "An error ocurred during login"}), 500

@api.get('/logout', summary="Logout user",
    description="Clears the user session and redirects to Auth0 logout."
)
def logout():
    """ Logout user """
    session.clear()
    params = {
        'returnTo': request.url_root,
        'client_id': current_app.config['CLIENT_ID']
    }
    auth0_domain = current_app.config['AUTH0_DOMAIN']
    return redirect(f'https://{auth0_domain}/v2/logout?{urlencode(params)}')

@api.get('/session', tags=[admin_tag], summary="Get current session info",
    security=[{"bearerAuth": []}],
    description="Retrieves information about the current user session.",
    responses={
        200: {"description": "Returns session information for authenticated user"},
        401: {"description": "User not authenticated"},
    }
)
@requires_auth
@requires_admin
def get_session():
    """ Get current session info """
    user = session.get('user', None)
    if user:
        return jsonify({
            'authenticated': True,
            'user': user,
            'access_token': user.get('access_token')  
        }), 200
    return jsonify({
        'authenticated': False,
        'user': None
    }), 401
    
@api.get('/admin/users', tags=[admin_tag], summary="Get all users info",
    security=[{"bearerAuth": []}],
    description="Retrieves information about all users. Admin access required.",
    responses={
        200: {"description": "Returns information for all users"},
        401: {"description": "User not authenticated"},
        403: {"description": "User not authorized (not an admin)"},
    }
)
@requires_auth
@requires_admin
def get_all_users_info():
    users = User.query.all()
    users_info = [{
        'user_id': user.id,
        'email': user.email,
        'name': user.name,
        'is_admin': user.is_admin,
        'access_token': session.get('user', {}).get('access_token') if user.id == g.current_user.id else None
    } for user in users]
    
    return jsonify({
        'users': users_info
    }), 200