from flask import Blueprint, request, jsonify
from extension import db
from models import Contribution
from flask_jwt_extended import jwt_required, get_jwt_identity
from utilis.auth import role_required

contribution_bp = Blueprint('contributions', __name__)

# ================================
# Get all contributions
# ================================
@contribution_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('admin', 'treasurer')
def get_all_contributions():
    contributions = Contribution.query.all()
    return jsonify([{
        'id': c.id,
        'member_id': c.user_id,
        'amount': c.amount,
        'date': c.date.strftime('%Y-%m-%d')
    } for c in contributions])

# ================================
# Get contributions by member
# ================================
@contribution_bp.route('/member/<int:member_id>/', methods=['GET'])
@jwt_required()
def get_contributions_by_member(member_id):
    contributions = Contribution.query.filter_by(user_id=member_id).all()
    return jsonify([{
        'id': c.id,
        'member_id': c.user_id,
        'amount': c.amount,
        'date': c.date.strftime('%Y-%m-%d')
    } for c in contributions])

# ================================
# Add a contribution
# ================================
@contribution_bp.route('/', methods=['POST'])
@jwt_required()
def add_contribution():
    data = request.json
    new_contribution = Contribution(user_id=data['member_id'], amount=data['amount'])
    db.session.add(new_contribution)
    db.session.commit()
    return jsonify(message='Contribution added successfully'), 201

# ================================
# Update a contribution
# ================================
@contribution_bp.route('/<int:id>/', methods=['PUT'])
@jwt_required()
def update_contribution(id):
    data = request.json
    contribution = Contribution.query.get(id)
    if not contribution:
        return jsonify(message='Contribution not found'), 404

    contribution.amount = data['amount']
    db.session.commit()
    return jsonify(message='Contribution updated successfully')

# ================================
# Delete a contribution
# ================================
@contribution_bp.route('/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_contribution(id):
    contribution = Contribution.query.get(id)
    if not contribution:
        return jsonify(message='Contribution not found'), 404

    db.session.delete(contribution)
    db.session.commit()
    return jsonify(message='Contribution deleted successfully')

# ================================
# Get total contributions (for dashboard)
# ================================
@contribution_bp.route('/total/', methods=['GET'])
@jwt_required()
def get_total_contributions():
    total = db.session.query(db.func.sum(Contribution.amount)).scalar() or 0
    return jsonify({'total_contributions': total})
