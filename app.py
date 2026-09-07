from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import or_
from models import db, Product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

ADMIN_KEY = "admin-secret-key-12345"

with app.app_context():
    db.create_all()

def verify_admin():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    return token == ADMIN_KEY

@app.route('/')
def home():
    return {"message": "Product Catalog API is running"}

@app.route('/products', methods=['POST'])
def create_product():
    if not verify_admin():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data.get('name') or data.get('price') is None or not data.get('category'):
        return jsonify({"error": "name, price, and category are required"}), 400

    product = Product(
        name=data['name'],
        price=data['price'],
        category=data['category'],
        images=",".join(data.get('images', [])),
        stock=data.get('stock', 0)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict())

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if not verify_admin():
        return jsonify({"error": "Unauthorized"}), 401

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.category = data.get('category', product.category)
    if 'images' in data:
        product.images = ",".join(data['images'])
    product.stock = data.get('stock', product.stock)

    db.session.commit()
    return jsonify(product.to_dict())

@app.route('/products/<int:product_id>',