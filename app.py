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

def paginate(query):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "products": [p.to_dict() for p in items]
    }

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

    if data.get('price') < 0:
        return jsonify({"error": "price cannot be negative"}), 400

    if data.get('stock', 0) < 0:
        return jsonify({"error": "stock cannot be negative"}), 400

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
    query = Product.query
    return jsonify(paginate(query))

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

    if 'price' in data and data['price'] < 0:
        return jsonify({"error": "price cannot be negative"}), 400

    if 'stock' in data and data['stock'] < 0:
        return jsonify({"error": "stock cannot be negative"}), 400

    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.category = data.get('category', product.category)
    if 'images' in data:
        product.images = ",".join(data['images'])
    product.stock = data.get('stock', product.stock)

    db.session.commit()
    return jsonify(product.to_dict())

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if not verify_admin():
        return jsonify({"error": "Unauthorized"}), 401

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

@app.route('/search', methods=['GET'])
def search_products():
    search = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock_only = request.args.get('in_stock', 'false').lower() == 'true'
    sort_by = request.args.get('sort_by', '')
    order = request.args.get('order', 'asc')

    query = Product.query

    if search:
        query = query.filter(or_(
            Product.name.ilike(f'%{search}%'),
            Product.category.ilike(f'%{search}%')
        ))

    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if in_stock_only:
        query = query.filter(Product.stock > 0)

    if sort_by in ['price', 'name', 'stock']:
        column = getattr(Product, sort_by)
        query = query.order_by(column.desc() if order == 'desc' else column.asc())

    return jsonify(paginate(query))

if __name__ == '__main__':
    app.run(debug=True)