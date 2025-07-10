from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from extension import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify(message='Username already exists'), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    new_user = User(
        fullName=data['fullName'],  # ✅ Make sure this is 'fullName' in both model and frontend
        username=data['username'],
        email=data['email'],
        phone=data['phone'],
        gender=data['gender'],
        role=data['role'],
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='User registered successfully'), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify(
            access_token=access_token,
            role=user.role,
            member_id=user.id,
            fullname=user.fullName  # ✅ Added fullname to response
        )
    return jsonify(message='Invalid credentials'), 401
