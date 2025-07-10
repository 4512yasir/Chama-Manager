from flask import Blueprint, request, jsonify
from extension import db
from models import User
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash
from utilis.auth import role_required

members_bp = Blueprint('members', __name__)

# ===========================
# Get all members
# ===========================
@members_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_members():
    members = User.query.all()
    return jsonify([
        {
            'id': m.id,
            'fullName': m.fullName,
            'username': m.username,
            'email': m.email,
            'phone': m.phone,
            'gender': m.gender,
            'role': m.role
        } for m in members
    ])


# ===========================
# Add a new member
# ===========================
@members_bp.route('/add/', methods=['POST'])
@jwt_required()
@role_required('admin')
def add_member():
    data = request.json

    required_fields = ['fullName', 'username', 'email', 'password', 'role', 'gender']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify(message=f'{field} is required'), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify(message='Username already exists'), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify(message='Email already exists'), 400

    new_user = User(
        fullName=data['fullName'],
        username=data['username'],
        email=data['email'],
        phone=data.get('phone', ''),
        gender=data['gender'],
        password=generate_password_hash(data['password'], method='pbkdf2:sha256'),
        role=data['role']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'Member added successfully',
        'member': {
            'id': new_user.id,
            'fullName': new_user.fullName,
            'username': new_user.username,
            'email': new_user.email,
            'phone': new_user.phone,
            'gender': new_user.gender,
            'role': new_user.role
        }
    }), 201


# ===========================
# Remove a member
# ===========================
@members_bp.route('/remove/<int:id>/', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def remove_member(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify(message='Member removed successfully')
    return jsonify(message='User not found'), 404


# ===========================
# Update a member
# ===========================
@members_bp.route('/update/<int:id>/', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_member(id):
    user = User.query.get(id)
    if not user:
        return jsonify(message='User not found'), 404

    data = request.json

    # Optional: Prevent username/email duplication if being changed
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify(message='Username already exists'), 400
        user.username = data['username']

    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify(message='Email already exists'), 400
        user.email = data['email']

    # Update other fields if provided
    user.fullName = data.get('fullName', user.fullName)
    user.phone = data.get('phone', user.phone)
    user.gender = data.get('gender', user.gender)
    user.role = data.get('role', user.role)

    # Optional: Update password if provided
    if 'password' in data and data['password']:
        user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    db.session.commit()

    return jsonify(message='Member updated successfully'), 200
