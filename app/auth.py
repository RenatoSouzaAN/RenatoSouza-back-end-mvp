"""
auth.py

This module handles the authentication and authorization mechanisms for the application.

It includes the following:
- Authentication of users using JWT tokens.
- Authorization checks for different user roles.
- Error handling related to authentication failures.

Functions:
- verify_token: Validates the JWT token.
- requires_auth: Decorator to protect routes with authentication.

Classes:
- AuthError: Custom exception class for authentication errors.
"""

import json
import logging

from functools import wraps
from urllib.request import urlopen
from flask import request, g, abort, session
from jose import jwt
from jose.exceptions import JWTError

from config import Config
from .models import User
from .extensions import db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

AUTH0_DOMAIN = Config.AUTH0_DOMAIN
ALGORITHMS = ["RS256"]
API_AUDIENCE = Config.API_AUDIENCE

class AuthError(Exception):
    """Exception raised for errors in the authentication process."""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    logger.debug("Request headers: %s", request.headers)
    auth = request.headers.get("Authorization", None)
    if not auth:
        logger.debug("No Authorization header present, checking session")
        if 'user' in session and 'access_token' in session['user']:
            return session['user']['access_token']
        logger.error("No Authorization header or session token present")
        raise AuthError({"code": "authorization_header_missing",
                         "description": "Authorization header is expected"}, 401)

    parts = auth.split()
    logger.debug("Authorization header parts: %s", parts)

    if parts[0].lower() != "bearer":
        logger.error("Authorization header must start with Bearer")
        raise AuthError({"code": "invalid_header",
                         "description": "Authorization header must start with Bearer"}, 401)
    if len(parts) == 1:
        logger.error("Token not found")
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    if len(parts) > 2:
        logger.error("Authorization header must be Bearer token")
        raise AuthError({"code": "invalid_header",
                         "description": "Authorization header must be Bearer token"}, 401)

    token = parts[1]

    return token

def get_or_create_user(payload):
    """Check if a user exists and creates it in case not"""
    logger.debug("Attempting to get or create user with payload: %s", payload)
    user_id = payload['sub']
    user = User.query.get(user_id)
    if not user:
        logger.info("User %s not found. Creating new user.", user_id)
        email = payload.get('email', '')
        name = payload.get('name') or None
        user = User(user_id=user_id, email=email, name=name)
        try:
            db.session.add(user)
            db.session.commit()
            logger.info("User %s created successfully.", user_id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating user: %s", user_id, str(e))
            raise
    else:
        logger.info("User %s already exists.", user_id)
    return user

def requires_auth(f):
    """Determines if the Access Token is valid"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        try:
            payload = verify_jwt(token)
        except Exception as e:
            logger.error("Error verifying JWT: %s", str(e))
            raise AuthError({"code": "invalid_token",
                                 "description": str(e)}, 401) from e

        g.current_user = get_or_create_user(payload)
        return f(*args, **kwargs)
    return decorated

def verify_jwt(token):
    """Verifies the JWT token"""
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    with urlopen(jwks_url) as response:
        jwks = json.loads(response.read())

    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        except JWTError as e:
            raise AuthError({"code": "invalid_token",
                             "description": str(e)}, 401) from e
    raise AuthError({"code": "invalid_header",
                     "description": "Unable to find appropriate key"}, 401)

def requires_admin(f):
    """Determines if the user is an admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            logger.error("No current user set in context")
            abort(401)

        user = g.current_user
        logger.debug("Checking admin status for user: %s", user.user_id)

        if user and user.is_admin:
            logger.info("Admin access granted for user: %s", user.user_id)
            return f(*args, **kwargs)

        logger.warning("Admin access denied for user: %s", user.user_id)
        abort(403)
    return decorated
