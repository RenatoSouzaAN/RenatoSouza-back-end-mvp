# DMarket API

DMarket API is a Flask-based RESTful API for managing products in a market database. It is made to fullfill the requirements in the 'Assessment Requirements and Composition', in which includes to perform some CRUD operations (Create, Read, and Delete) on products stored in an SQLite database, with its data documented in Swagger, whilst being a SPA (Single Page Application).  -- The front-end has it own repository, the link for is below --


Front-end repository: https://github.com/RenatoSouzaAN/RenatoSouza/front-end-mvp

## Features

- List all products
- Add a new product
- Delete a product

## Setup

### Prerequisites

- Python 3.x installed
- Pip package manager

### Installation

It's highly recommended to use a virtual environment.

1. Clone the repository:
   ```
   git clone <repository_url>
   cd dmarket-api
   ```

2. Create virtual environment (Optional): 
   ```
   python -m venv env
   ```

3. Access virtual environment (Optional): 
   
   On Powershell:
   ```
   .\env\Scripts\activate
   ```
   On bash:
   ```
   source \env\Scripts\activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```


### Explanation:

These commands (`flask db init`, `flask db migrate`, `flask db upgrade`) are used with Flask-Migrate to initialize a migrations directory, generate migration scripts based on changes in your models, and apply those migrations to your database schema.

- **`flask db init`**: Initializes a new migration repository in your project, creating a `migrations` directory where migration scripts will be stored.
  
- **`flask db migrate`**: Analyzes the current state of your models and generates a migration script that outlines the changes needed to synchronize the database schema with the current state of your models.
  
- **`flask db upgrade`**: Applies the migration script to the database, making the necessary changes to the schema to reflect the changes in your models.

These steps are crucial whenever you make changes to your database models (`models.py` in this case) to ensure that your database schema stays up-to-date with your application's data model.

### Running the Server

To start the Flask server:
```
flask run
```

The API will be accessible at `http://localhost:5000`.

### API Documentation

Swagger UI is integrated for API documentation. Visit `http://localhost:5000/swagger` after starting the server to explore the API endpoints and interact with them. You can also visit `http://localhost:5000/` and be redirected to the Swagger UI.

## API Endpoints

### Get all products

- **GET** `/products`
  - Returns a list of all products in the database.

### Add a product

- **POST** `/products`
  - Adds a new product to the database. Requires JSON payload with `name`, `price`, and `quantity`.

### Delete a product

- **DELETE** `/products/<product_id>`
  - Deletes the product with the specified `product_id` from the database.

## Responses

- Successful responses include appropriate HTTP status codes and JSON payloads.
- Error responses provide meaningful error messages and status codes.

## Technology Stack

- **Flask**: Micro web framework for Python
- **Flask-SQLAlchemy**: SQLAlchemy extension for Flask
- **Flask-Migrate**: Database migrations for Flask applications
- **Flask-CORS**: CORS support for Flask
- **Flask-Swagger-UI**: Swagger UI integration for API documentation

## Contributors

- Renato Souza de Almeida Neto <renatosouza.an@gmail.com>

## License

This project is licensed under the MIT License - see the [LICENSE](RenatoSouza-back-end-mvp\LICENSE) file for details.