from flask import jsonify, redirect, request, url_for, session, current_app, g, abort
from jose import jwt
from jose.exceptions import JWTError
from urllib.parse import urlencode
from . import oauth
from .auth import requires_auth, requires_admin, AuthError, get_token_auth_header, get_or_create_user, verify_jwt
from config import Config
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel

from .models import Product, User
from .schemas import ProductInput, GetProduct, ProductUpdate, MessageResponse, AdminSetBody
from . import db
import logging
import traceback
import base64
import json

api = APIBlueprint('api', __name__)

product_tag = Tag(name='product', description='Product operations')
admin_tag = Tag(name='admin', description='Admin operations')

logger = logging.getLogger(__name__)
class ProductIdPath(BaseModel):
    product_id: int

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

#@api.post('/admin/set', tags=[admin_tag])
@api.post('/admin/set', tags=[admin_tag])
@requires_auth
# @requires_admin
def set_admin(body: AdminSetBody):
    # Check if there are any existing admins
    existing_admin = User.query.filter_by(is_admin=True).first()
    
    # If there are existing admins, only allow current admins to set new admins
    if existing_admin and not g.current_user.is_admin:
        return jsonify({'message': 'Only existing admins can set new admins'}), 403
    
    user = User.query.filter_by(email=body.email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.is_admin = True
    db.session.commit()
    return jsonify({'message': 'User set as admin successfully'}), 200

@api.get('/admin/check')
@requires_auth
def check_admin():
    return jsonify({'is_admin': g.current_user.is_admin}), 200

@api.get('/login')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("api.callback", _external=True),
        # audience=f'https://{Config.AUTH0_DOMAIN}/userinfo',
        audience=Config.API_AUDIENCE,
        scope="openid profile email"
    )

@api.get('/callback')
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        
        # Get user info from Auth0
        userinfo_endpoint = f"https://{Config.AUTH0_DOMAIN}/userinfo"
        resp = oauth.auth0.get(userinfo_endpoint)
        userinfo = resp.json()

        # Save or update user in database
        user = get_or_create_user(userinfo)

        session['user'] = {
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'access_token': token['access_token']
        }

        logger.info(f"User logged in and saved to database: {user}")
        return redirect("/")
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An error ocurred during login"}), 500

@api.get('/logout')
def logout():
    session.clear()
    params = {
        # 'returnTo': url_for('index', _external=True),
        'returnTo': request.url_root,
        'client_id': current_app.config['CLIENT_ID']
    }
    auth0_domain = current_app.config['AUTH0_DOMAIN']
    return redirect(f'https://{auth0_domain}/v2/logout?{urlencode(params)}')

@api.get('/session')
def get_session():
    user = session.get('user', None)
    if user:
        return jsonify({
            'authenticated': True,
            'user': user,
            'access_token': user.get('access_token')  # Include access token in the response
        }), 200
    return jsonify({
        'authenticated': False,
        'user': None
    }), 401

@api.route('/test_user_creation')
def test_user_creation():
    try:
        user = User(id='test1234', email='test2@test.com', name='')
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@api.route('/test_product_creation')
def test_product_creation():
    try:
        product = Product(name='test product', description="", price=10, quantity=5, user_id='testuserid')
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@api.route('/test_db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"message": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api.get('/inspect_token', security=[{"bearerAuth": []}])
@requires_auth
def inspect_token():
    try:
        user = g.get('current_user')
        if user is None:
            logger.error("current user not found in g")
            return jsonify({"error": "User not found"}), 404

        user_dict = user.to_dict() if hasattr(user, 'to_dict') else str(user)
        token_payload = g.get('token_payload', {})

        return jsonify({
            "message": "Token inspection successful",
            "user": user_dict,
            "token_payload": token_payload
        }), 200
    except Exception as e:
        logger.error(f"Error in inspect_token: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An error occurred while processing the request"}), 500

@api.get('/test_auth_header', security=[{"bearerAuth": []}])
def test_auth_header():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        return jsonify({"message": "Authorization header found", "header": auth_header}), 200
    else:
        return jsonify({"message": "No Authorization header found"}), 401
    
@api.get('/test_token', security=[{"bearerAuth": []}])
@requires_auth
def test_token():
    try:
        token = get_token_auth_header()
        logger.debug(f"Token received in test_token: {token[:10]}...")

        # Attempt to decode the token
        try:
            # Decode and verify the JWT
            # unverified_claims = jwt.get_unverified_claims(token)
            payload = verify_jwt(token)
            return jsonify({"message": "Token decoded successfully", "claims": payload}), 200
        except JWTError as e:
            logger.error(f"JWTError in test_token: {str(e)}")
            return jsonify({"error": "Invalid JWT token"}), 401
        
    except AuthError as ae:
        logger.error(f"AuthError in test_token: {ae.error}")
        return jsonify(ae.error), ae.status_code
    except Exception as e:
        logger.error(f"Unexpected error in test_token: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    
@api.get('/user')
def get_user():
    if 'user' in session:
        return jsonify(session['user']), 200
    return jsonify({"message": "User not logged in"}), 401

@api.get('/echo_token')
@requires_auth
def echo_token():
    auth_header = request.headers.get('Authorization', '')
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        token = parts[1]
        return jsonify({
            "received_token": token,
            "token_length": len(token),
            "token_type": str(type(token))
        }), 200
    else:
        return jsonify({"error": "Invalid Authorization header"}), 400
    
@api.get('/inspect_token2')
def inspect_token2():
    try:
        token = get_token_auth_header()

        # Decode the token header
        header_segment = token.split('.')[0]
        padded = header_segment + '=' * (4 - len(header_segment) % 4)
        header = json.loads(base64.b64decode(padded).decode('utf-8'))

        if header.get('enc') == 'A256GCM':
            # This is a JWE token
            return jsonify({"message": "Ecrypted token detected", 
                            "header": header,
                            "note": "This is a JWE (JSON Web Encryption) token. Decryption requires the appropriate key."
                            }), 200

        else:
            # Attempt to decode as a regular JWT
            decoded = jwt.decode(token, verify=False)
            return jsonify({
                "message": "Token inspection",
                "header": header,
                "payload": decoded
            }), 200
    except AuthError as e:
        return jsonify(e.error), e.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 400