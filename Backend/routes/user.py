from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from utilis.decorator import role_required

user_bp = Blueprint('user', __name__)

# Admin: Get all users
@user_bp.route('/', methods=['GET'])
@jwt_required()
@role_required("admin")
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'username': user.username,
        'role': user.role,
        'organization': user.organization.name
    } for user in users]), 200

# Admin: Get user by ID
@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required("admin")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'username': user.username,
        'role': user.role,
        'organization': user.organization.name
    }), 200

# Admin: Delete user
@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

# Admin: Update any user
@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required("admin")
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.username = data.get('username', user.username)
    user.role = data.get('role', user.role)

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "organization": user.organization.name
        }
    }), 200

# Member/Admin: View own profile
@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_own_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "username": user.username,
        "phone": user.phone,
        "profile_image": user.profile_image,
        "role": user.role,
        "organization": user.organization.name
    }), 200

# Member/Admin: Update own profile
@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.username = data.get('username', user.username)
    user.phone = data.get('phone', user.phone)
    user.profile_image = data.get('profile_image', user.profile_image)

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "phone": user.phone,
            "profile_image": user.profile_image
        }
    }), 200
