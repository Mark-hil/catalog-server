from flask import jsonify, request
from . import app, db
from .models import Product, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from elasticsearch import Elasticsearch

# Catalog Endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price} for p in products])

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({'id': product.id, 'name': product.name, 'description': product.description, 'price': product.price})

# Signup Endpoint
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if the user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    # Create a new user
    new_user = User(username=username)
    new_user.set_password(password)  # Hash the password
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

# Login Endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Find the user
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate a JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

# Protected Endpoint (Example)
@app.route('/api/protected', methods=['GET'])
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