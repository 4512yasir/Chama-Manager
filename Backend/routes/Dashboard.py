from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Loan, Contribution, Organization

dash_bp = Blueprint('dashboard', __name__)

@dash_bp.route('/user', methods=['GET'])
@jwt_required()
def user_dashboard():
    user_id = get_jwt_identity()
    loans = Loan.query.filter_by(user_id=user_id).count()
    contributions = Contribution.query.filter_by(user_id=user_id).count()

    return jsonify({
        'total_loans': loans,
        'total_contributions': contributions
    }), 200

@dash_bp.route('/admin', methods=['GET'])
@jwt_required()
def admin_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'msg': 'Unauthorized'}), 403

    members = User.query.filter_by(organization_id=user.organization_id).count()
    total_loans = Loan.query.count()
    total_contributions = Contribution.query.count()

    return jsonify({
        'total_members': members,
        'total_loans': total_loans,
        'total_contributions': total_contributions
    }), 200

@dash_bp.route('/system', methods=['GET'])
@jwt_required()
def system_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'system':
        return jsonify({'msg': 'Unauthorized'}), 403

    total_users = User.query.count()
    total_orgs = Organization.query.count()
    total_loans = Loan.query.count()
    total_contributions = Contribution.query.count()

    return jsonify({
        'total_users': total_users,
        'total_organizations': total_orgs,
        'total_loans': total_loans,
        'total_contributions': total_contributions
    }), 200