from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import or_
from dotenv import load_dotenv
import os

from models import db, Product


load_dotenv()

ADMIN_KEY = os.getenv("ADMIN_KEY")


app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


with app.app_context():
    db.create_all()


def verify_admin():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return False

    token = auth_header.split(" ")[1]

    return token == ADMIN_KEY


def paginate(query):
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    if page < 1:
        page = 1

    if limit < 1:
        limit = 10

    products = query.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )

    return products


@app.route("/")
def home():
    return jsonify({
        "message": "Monish Jewelry Product Catalog API",
        "status": "running"
    })


@app.route("/products", methods=["POST"])
def create_product():

    if not verify_admin():
        return jsonify({
            "error": "Unauthorized"
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    name = data.get("name")
    price = data.get("price")
    category = data.get("category")
    images = data.get("images", [])
    stock = data.get("stock", 0)

    if not name or not category or price is None:
        return jsonify({
            "error": "name, price and category are required"
        }), 400

    if price < 0:
        return jsonify({
            "error": "Price cannot be negative"
        }), 400

    if stock < 0:
        return jsonify({
            "error": "Stock cannot be negative"
        }), 400

    if isinstance(images, list):
        images = ",".join(images)

    product = Product(
        name=name,
        price=price,
        category=category,
        images=images,
        stock=stock
    )

    db.session.add(product)
    db.session.commit()

    return jsonify(product.to_dict()), 201


@app.route("/products", methods=["GET"])
def get_products():

    query = Product.query

    paginated = paginate(query)

    return jsonify({
        "total": paginated.total,
        "total_pages": paginated.pages,
        "page": paginated.page,
        "limit": paginated.per_page,
        "products": [
            product.to_dict()
            for product in paginated.items
        ]
    })


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify(product.to_dict())


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):

    if not verify_admin():
        return jsonify({
            "error": "Unauthorized"
        }), 401

    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "name" in data:
        product.name = data["name"]

    if "price" in data:
        if data["price"] < 0:
            return jsonify({
                "error": "Price cannot be negative"
            }), 400

        product.price = data["price"]

    if "category" in data:
        product.category = data["category"]

    if "images" in data:
        images = data["images"]

        if isinstance(images, list):
            images = ",".join(images)

        product.images = images

    if "stock" in data:
        if data["stock"] < 0:
            return jsonify({
                "error": "Stock cannot be negative"
            }), 400

        product.stock = data["stock"]

    db.session.commit()

    return jsonify(product.to_dict())


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):

    if not verify_admin():
        return jsonify({
            "error": "Unauthorized"
        }), 401

    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({
        "message": "Product deleted successfully"
    })


@app.route("/search", methods=["GET"])
def search_products():

    query = Product.query

    search = request.args.get("q")
    category = request.args.get("category")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    in_stock = request.args.get("in_stock")

    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.category.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(
            Product.category.ilike(f"%{category}%")
        )

    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    if in_stock == "true":
        query = query.filter(Product.stock > 0)

    elif in_stock == "false":
        query = query.filter(Product.stock == 0)

    sort_by = request.args.get("sort_by")
    order = request.args.get("order", "asc")

    if sort_by == "price":
        sort_column = Product.price

    elif sort_by == "name":
        sort_column = Product.name

    elif sort_by == "stock":
        sort_column = Product.stock

    else:
        sort_column = Product.id

    if order == "desc":
        query = query.order_by(sort_column.desc())

    else:
        query = query.order_by(sort_column.asc())

    paginated = paginate(query)

    return jsonify({
        "total": paginated.total,
        "total_pages": paginated.pages,
        "page": paginated.page,
        "limit": paginated.per_page,
        "products": [
            product.to_dict()
            for product in paginated.items
        ]
    })


if __name__ == "__main__":
    app.run(debug=True)