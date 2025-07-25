# auth.py
from flask import Blueprint, request, jsonify
from models import db, User, Organization
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'member').lower()
    org_name = data.get('organization')

    if not all([name, email, username, password, org_name]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check or create organization
    organization = Organization.query.filter_by(name=org_name).first()
    if not organization:
        organization = Organization(name=org_name)
        db.session.add(organization)
        db.session.commit()

    # Check if username/email already exists in that organization
    existing_user = User.query.filter_by(username=username, organization_id=organization.id).first()
    if existing_user:
        return jsonify({'error': 'Username already exists in this organization'}), 400

    user = User(
        name=name,
        email=email,
        username=username,
        role=role,
        organization_id=organization.id
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username')
    password = data.get('password')
    org_name = data.get('organization')

    if not all([username_or_email, password, org_name]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Ensure org exists
    organization = Organization.query.filter_by(name=org_name).first()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404

    # Look for user by username or email in the org
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email),
        User.organization_id == organization.id
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(
        identity={'id': user.id, 'role': user.role, 'org': organization.name},
        expires_delta=timedelta(hours=12)
    )

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'role': user.role,
            'organization': organization.name
        }
    }), 200
