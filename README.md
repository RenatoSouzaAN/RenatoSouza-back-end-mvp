# Back-End (API)

This API is a Flask-based RESTful API for managing products in a market database. It includes user authentication, admin functionality, and CRUD operations for products. The API is documented using OpenAPI 3 and is designed to work with a separate front-end application. -- The front-end has it own repository, the link for is below --

Front-end repository: https://github.com/RenatoSouzaAN/RenatoSouza/front-end-mvp

## Table of Contents

-   [Features](#features)
-   [Technology Stack](#technology-stack)
-   [Setup](#setup)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
    -   [Explanation](#explanation)
-   [Running the Server](#running-the-server)
-   [API Documentation](#api-documentation)
-   [API Endpoints](#api-endpoints)
    -   [Get all products](#get-all-products)
    -   [Add a product](#add-a-product)
    -   [Update a product](#update-a-product)
    -   [Delete a product](#delete-a-product)
    -   [Set user as an admin](#set-user-as-an-admin)
    -   [Login into an account](#login-into-an-account)
    -   [Logout from account](#logout-from-account)
    -   [Get all users](#get-all-users)
-   [Responses](#responses)
-   [Authentication](#authentication)
-   [Contributors](#contributors)
-   [License](#license)

## Features

-   User authentication with Auth0
-   Admin user management
-   CRUD operations for products
-   User-specific product management
-   OpenAPI 3 documentation

## Technology Stack
This back-end is built using the following technologies:

-   **Flask**: Micro web framework for Python.
-   **Flask-SQLAlchemy**: SQLAlchemy extension for Flask.
-   **Flask-Migrate**: Database migrations for Flask applications.
-   **Flask-CORS**: CORS support for Flask.
-   **Flask-OpenAPI3**: OpenAPI 3 integration for API documentation.
-   **Authlib**: OAuth and OpenID Connect library for Python.
-   **SQLite**: Lightweight, serverless database engine.

## Setup

### Prerequisites

-   Python 3.x installed
-   Pip package manager
-   Auth0 account and application setup

### Installation

It's highly recommended to use a virtual environment.

1. Clone the repository:

    ```
    git clone https://github.com/RenatoSouzaAN/RenatoSouza-back-end-mvp.git
    cd RenatoSouza-back-end-mvp
    ```

2. Create a `.env` file in the root directory with the following content:
   ```
   AUTH0_DOMAIN=your_auth0_domain
   API_AUDIENCE=your_api_audience
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   AUTH0_MANAGEMENT_CLIENT_ID=your-auth0-management-client-id
   AUTH0_MANAGEMENT_CLIENT_SECRET=your-auth0-management-client-secret
   ```

3. Create virtual environment (Optional):

    ```
    python -m venv env
    ```

4. Access virtual environment (Optional):

    On Powershell:

    ```
    .\env\Scripts\activate
    ```

    On bash:

    ```
    source \env\Scripts\activate
    ```

5. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

6. Set up the database:
    ```
    flask db init
    flask db migrate
    flask db upgrade
    ```

### Explanation:

These commands (`flask db init`, `flask db migrate`, `flask db upgrade`) are used with Flask-Migrate to initialize a migrations directory, generate migration scripts based on changes in your models, and apply those migrations to your database schema.

-   **`flask db init`**: Initializes a new migration repository in your project, creating a `migrations` directory where migration scripts will be stored.
-   **`flask db migrate`**: Analyzes the current state of your models and generates a migration script that outlines the changes needed to synchronize the database schema with the current state of your models.
-   **`flask db upgrade`**: Applies the migration script to the database, making the necessary changes to the schema to reflect the changes in your models.

These steps are crucial whenever you make changes to your database models (`models.py` in this case) to ensure that your database schema stays up-to-date with your application's data model.

### Running the Server

To start the Flask server:

```
flask run
```

or

```
python run.py
```

The API will be accessible at `http://localhost:5000`.

### API Documentation

OpenAPI 3 is integrated for API documentation. After starting the server, visit http://localhost:5000/openapi to explore the API endpoints and interact with them.

## Key API Endpoints

### Get all products

-   **GET** `/products`
    -   Returns a list of all products in the database.

### Add a product

-   **POST** `/products/create`
    -   Adds a new product to the database. Requires JSON payload with `name`, `price`, and `quantity`. (authenticated)

### Update a product

-   **PUT** `/products/<product_id>/update`
    -   Upgrades the product with the specified `product_id` from the database. Requires a JSON payload with any of the following fields: description, price, or quantity. (authenticated)

### Delete a product

-   **DELETE** `/products/<product_id>/delete`
    -   Deletes the product with the specified `product_id` from the database. (authenticated)

### Set user as an admin
-   **POST** `/admin/set`
    -   Changes the privileges of a user by setting it as an admin (authenticaded) (admin only)

### Login into an account
-   **GET** `/login`
    -   Initiate login process by requesting authentication through Auth0 API

### Logout from account
-   **GET** `/logout`
    -   Logs out the current logged user by requesting Auth0 API

### Get all users
-   **GET** `/admin/users`
    -   Returns a list of all user in the database. (authenticaded) (admin only)

## Responses

-   Successful responses include appropriate HTTP status codes and JSON payloads.
-   Error responses provide meaningful error messages and status codes.

## Authentication

This API uses Auth0 for authentication. Users need to authenticate through the `/login` endpoint, which will redirect to Auth0 for login. After successful authentication, users receive a JWT token which should be included in the `Authorization` header for authenticated requests.

## Contributors

-   Renato Souza de Almeida Neto <renatosouza.an@gmail.com>

## License

This project is licensed under the MIT License - see the [LICENSE](RenatoSouza-back-end-mvp\LICENSE) file for details.
