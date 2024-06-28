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
        

    @app.route('/products/create', methods = ['POST'])
    def add_product():
        """Add a new product to the 'products' database

        Returns a message if the product was added or an error ocurred.
        """
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
        # if not data.get('price'):
        #     return jsonify({'message': 'Price is required'}), 400
        # if not data.get('quantity'):
        #     return jsonify({'message': 'Quantity is required'}), 400
        
        try:
            price = float(data['price'])
        except ValueError:
            return jsonify({'message': 'Price must be a number'}), 400
        
        try:
            quantity = int(data['quantity'])
        except ValueError:
            return jsonify({'message': 'Quantity must be a number'}), 400
        
        if price < 1:
            return jsonify({'message': 'Price must be higher than 0.'}), 400

        if quantity < 1:
            return jsonify({'message': 'Quantity must be higher than 0.'}), 400
        
        new_product = Product(
            name = data['name'],
            description = data.get('description', ''),
            price = price,
            quantity = quantity
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully!'}), 202
      
    @app.route('/products/<int:product_id>/update', methods=['PUT'])
    def update_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found.'}), 404
        
        data = request.get_json()
        
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            try:
                product.price = float(data['price'])
                price = product.price
                if price < 1:
                    return jsonify({'message': 'Price must be higher than 0.'}), 400
                # product.price = price
            except ValueError:
                return jsonify({'message': 'Price must be a number.'}), 400
        if 'quantity' in data:
            try:
                product.quantity = int(data['quantity'])
                quantity = product.quantity
                if quantity < 1:
                    return jsonify({'message': 'Quantity must be higher than 0.'}), 400
                # product.quantity = quantity
            except ValueError:
                return jsonify({'message': 'Price must be a number.'}), 400
            
        db.session.commit()
        return jsonify({'message': 'Product updated successfully.'}), 203

    
    @app.route('/products/<int:product_id>/delete', methods=['DELETE'])
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({'message': 'Product updated successfully.'}), 204
        return jsonify({'message': 'Product not found'}), 404