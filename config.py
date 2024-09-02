import os

class Config:
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'your-auth0-domain')
    API_IDENTIFIER = os.getenv('API_IDENTIFIER', 'your-api-identifier')
    API_AUDIENCE = os.getenv('API_AUDIENCE', 'your-api-audience')
    API_MANAGEMENT_AUDIENCE = os.getenv('API_MANAGEMENT_AUDIENCE', 'your-api-management-audience')
    CLIENT_ID = os.getenv('CLIENT_ID', 'your-client-id')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'your-client-secret')
    AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL', 'http://localhost:5000/callback')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    AUTH0_MANAGEMENT_CLIENT_ID= os.getenv('AUTH0_MANAGEMENT_CLIENT_ID', 'your-auth0-management-client-id')
    AUTH0_MANAGEMENT_CLIENT_SECRET = os.getenv('AUTH0_MANAGEMENT_CLIENT_SECRET', 'your-auth0-management-client-secret')