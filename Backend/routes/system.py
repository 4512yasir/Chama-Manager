from flask import Blueprint, jsonify
from models import Organization, User, Loan, Contribution
from flask_jwt_extended import jwt_required
from utilis.decorator import role_required

system_bp = Blueprint('system', __name__)

@system_bp.route('/organizations', methods=['GET'])
@jwt_required()
@role_required("system_operator")
def view_all_organizations():
    organizations = Organization.query.all()
    return jsonify([
        {
            "id": org.id,
            "name": org.name
        } for org in organizations
    ]), 200

@system_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required("system_operator")
def view_all_users():
    users = User.query.all()
    return jsonify([
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "organization": user.organization.name
        } for user in users
    ]), 200

@system_bp.route('/data', methods=['GET'])
@jwt_required()
@role_required("system_operator")
def view_system_data():
    loans = Loan.query.all()
    contributions = Contribution.query.all()

    return jsonify({
        "total_loans": len(loans),
        "total_contributions": len(contributions)
    }), 200
