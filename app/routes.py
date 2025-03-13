from flask import jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from sqlalchemy import func  # Import func for SQL functions

from . import app, db
from .models import Product, User

# from elasticsearch import Elasticsearch


# Catalog Endpoints
@app.route("/api/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify(
        [
            {"id": p.id, "name": p.name, "description": p.description, "price": p.price}
            for p in products
        ]
    )


@app.route("/api/products/<int:id>", methods=["GET"])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
        }
    )


# Signup Endpoint
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Check if the user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    # Create a new user
    new_user = User(username=username)
    new_user.set_password(password)  # Hash the password
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# Search Endpoint with Enhanced Functionality
@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": 'Query parameter "q" is required'}), 400

    # Get pagination parameters (default to page 1 and 10 items per page)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Perform a full-text search with ranking and pagination
    search_results = (
        Product.query.filter(
            Product.search_vector.match(query, postgresql_regconfig="english")
        )
        .order_by(
            func.ts_rank(
                Product.search_vector, func.to_tsquery("english", query)
            ).desc()
        )
        .paginate(page=page, per_page=per_page)
    )

    # Format the results
    results = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
        }
        for product in search_results.items
    ]

    # Return the results with pagination metadata
    return jsonify(
        {
            "results": results,
            "total": search_results.total,
            "page": search_results.page,
            "per_page": search_results.per_page,
            "total_pages": search_results.pages,
        }
    )


# Login Endpoint
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Find the user
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate a JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


# Protected Endpoint (Example)
@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(logged_in_as=user.username), 200


# es = Elasticsearch()

# @app.route('/api/search', methods=['GET'])
# def search():
#     query = request.args.get('q')
#     results = es.search(index='products', body={'query': {'match': {'name': query}}})
#     return jsonify(results['hits']['hits'])
