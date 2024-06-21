from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from .models import Product

request_api = Blueprint('request_api', __name__)

def register_routes(app, db):
    CORS(app)

    @app.route('/products', methods = ['GET'])
    def get_products():
        products = Product.query.all()
        if len(products) == 0: 
            return jsonify({'message': 'The Products database is empty'}), 201
        else:
            products_list = [
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'quantity': product.quantity
                }
                for product in products
            ]
            return jsonify(products_list), 200
        

    @app.route('/products', methods = ['POST'])
    def add_product():
        """Add a new product to the 'products' database

        Returns a message if the product was added or an error ocurred.
        """
        data = request.get_json()
        #Certify that all required fields are filled
        if not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
        if not data.get('price'):
            return jsonify({'message': 'Price is required'}), 400
        if not data.get('quantity'):
            return jsonify({'message': 'Quantity is required'}), 400
        
        #Certify that the value inserted in the price field is a number
        try:
            price = float(data['price'])
        except ValueError:
            return jsonify({'message': 'Price must be a number'}), 400
        
        #Certify that the value inserted in the quantity field is a number
        try:
            quantity = int(data['quantity'])
        except ValueError:
            return jsonify({'message': 'Quantity must be a number'}), 400

        new_product = Product(
            name = data['name'],
            description = data.get('description', ''),
            price = price,
            quantity = quantity
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully!'}), 202

    @app.route('/products/<int:product_id>', methods=['DELETE'])
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return '', 204
        return jsonify({'message': 'Product not found'}), 404