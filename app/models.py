from .extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, nullable=False)
    description = db.Column(db.String(120))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)

    user = db.relationship('User', backref=db.backref('products', lazy=True))

    def __init__(self, name, description, price, quantity, user_id):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.user_id = user_id

    def __repr__(self):
        return f'<Product {self.name}>'
    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(64), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, id, email, name, is_admin=False):
        self.id = id
        self.email = email
        self.name = name
        self.is_admin = is_admin

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_admin': self.is_admin,
        }

    def __repr__(self):
        return f'<User {self.email}>'