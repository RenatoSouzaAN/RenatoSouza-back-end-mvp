import json
from flask import request, g, abort, session
from functools import wraps
from jose import jwt
from jose.exceptions import JWTError
from urllib.request import urlopen

from config import Config
from .models import User
from .extensions import db

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

AUTH0_DOMAIN = Config.AUTH0_DOMAIN
ALGORITHMS = ["RS256"]
API_AUDIENCE = Config.API_AUDIENCE

class AuthError(Exception):
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
    logger.debug(f"Authorization header parts: {parts}")

    if parts[0].lower() != "bearer":
        logger.error("Authorization header must start with Bearer")
        raise AuthError({"code": "invalid_header",
                         "description": "Authorization header must start with Bearer"}, 401)
    elif len(parts) == 1:
        logger.error("Token not found")
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        logger.error("Authorization header must be Bearer token")
        raise AuthError({"code": "invalid_header",
                         "description": "Authorization header must be Bearer token"}, 401)
    
    token = parts[1]

    return token

def get_or_create_user(payload):
    """Check if a user exists and creates it in case not"""
    logger.debug(f"Attempting to get or create user with payload: {payload}")
    user_id = payload['sub']
    user = User.query.get(user_id)
    if not user:
        logger.info(f"User {user_id} not found. Creating new user.")
        email = payload.get('email', '')
        name = payload.get('name') or None
        user = User(id=user_id, email=email, name=name)
        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"User {user_id} created successfully.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise
    else:
        logger.info(f"User {user_id} already exists.")
    return user

def requires_auth(f):
    """Determines if the Access Token is valid"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        try:
            payload = verify_jwt(token)
        except Exception as e:
            logger.error(f"Error verifying JWT: {str(e)}")
            raise AuthError({"code": "invalid_token",
                                 "description": str(e)}, 401)              
        
        g.current_user = get_or_create_user(payload)
        return f(*args, **kwargs)
    return decorated

def verify_jwt(token):
    """Verifies the JWT token"""
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
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
                             "description": str(e)}, 401)
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
        logger.debug(f"Checking admin status for user: {user}")
        
        if user and user.is_admin:
            logger.info(f"Admin access granted for user: {user.id}")
            return f(*args, **kwargs)
        
        logger.warning(f"Admin access denied for user: {user.id}")
        abort(403)
    return decorated