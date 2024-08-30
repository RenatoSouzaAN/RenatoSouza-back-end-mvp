"""
routes/auth.py
This module defines the Authentication API routes for the application.
It includes routes for:
- User management
Functions:
- create_user: Handles user creation.
- login: Initiate login process.
- logout: Initiate logout process.
- check_admin: Check if user is an admin.
- set_admin: Set a user as admin.
"""

from urllib.parse import urlencode

import json
import logging
import requests

from flask import jsonify, redirect, request, url_for, session, current_app, g
from flask_openapi3 import APIBlueprint, Tag
from config import Config

from ..extensions import db, oauth
from ..auth import requires_auth, requires_admin, get_or_create_user
from ..models.user import User
# from ..schemasOld import AdminSetBody
from ..schemas.admin import AdminSetBody

auth_bp = APIBlueprint('auth', __name__)

admin_tag = Tag(name='admin', description='Admin operations')

logger = logging.getLogger(__name__)

@auth_bp.post('/admin/set', tags=[admin_tag],
    summary="Set a user as admin",
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

@auth_bp.get('/admin/check', security=[{"bearerAuth": []}])
@requires_auth
def check_admin():
    """Check if user is an admin"""
    return jsonify({'is_admin': g.current_user.is_admin}), 200

@auth_bp.get('/login',
    summary="Initiate login process",
    description="Redirects the user to the Auth0 login page."
)
def login():
    """ Initiate login process """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True),
        audience=Config.API_AUDIENCE,
        scope="openid profile email"
    )

@auth_bp.get('/callback',
    summary="Auth0 callback",
    description="Handles the callback from Auth0 after user authentication."
)
def callback():
    """ Handles the callback from Auth0 after user authentication. """
    try:
        token = oauth.auth0.authorize_access_token()

        userinfo_endpoint = f"https://{Config.AUTH0_DOMAIN}/userinfo"
        resp = oauth.auth0.get(userinfo_endpoint)
        resp.raise_for_status()
        userinfo = resp.json()

        user = get_or_create_user(userinfo)

        session['user'] = {
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'access_token': token['access_token']
        }
        return redirect("/")
    except oauth.OAuth2Error as e:
        logger.error("OAuth error in callback: %s", str(e))
        return jsonify({"error": "OAuth authentication error"}), 500
    except requests.HTTPError as e:
        logger.error("HTTP error during user info fetch: %s", str(e))
        return jsonify({"error": "Failed to fetch user information"}), 500
    except json.JSONDecodeError as e:
        logger.error("Error decoding JSON response: %s", str(e))
        return jsonify({"error": "Failed to decode user information"}), 500
    except RuntimeError as e:
        logger.error("Unexpected error in callback: %s", str(e), exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

@auth_bp.get('/logout',
    summary="Logout user",
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

@auth_bp.get('/session', tags=[admin_tag],
    summary="Get current session info",
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

@auth_bp.get('/admin/users', tags=[admin_tag],
    summary="Get all users info",
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
    """ Get all users info """
    users = User.query.all()
    users_info = [
        {
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'is_admin': user.is_admin,
            'access_token': (
                session.get('user', {}).get('access_token')
                if user.user_id == g.current_user.user_id
                else None
            )
        }
        for user in users
    ]

    return jsonify({
        'users': users_info
    }), 200
