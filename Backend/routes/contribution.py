from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Contribution, Organization
from datetime import datetime
from sqlalchemy import extract

contribution_bp = Blueprint('contribution_bp', __name__)

# Simulated MPesa STK Push
def mock_stk_push(amount, phone):
    print(f"STK Push: Sending KES {amount} to {phone}")
    return {"status": "success", "message": "STK push initiated"}

@contribution_bp.route('/pay', methods=['POST'])
@jwt_required()
def make_contribution():
    data = request.get_json()
    amount = data.get('amount')
    phone = data.get('phone')

    if not amount or not phone:
        return jsonify({"error": "Amount and phone required"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Simulate STK push
    payment_response = mock_stk_push(amount, phone)

    if payment_response["status"] == "success":
        contribution = Contribution(
            amount=amount,
            user_id=user.id,
            organization_id=user.organization_id,
            status="completed"
        )
        db.session.add(contribution)
        db.session.commit()
        return jsonify({"message": "Contribution successful"}), 201
    else:
        return jsonify({"error": "STK push failed"}), 500

@contribution_bp.route('/my', methods=['GET'])
@jwt_required()
def my_contributions():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    contributions = Contribution.query.filter_by(user_id=user.id).all()
    return jsonify([
        {
            "amount": c.amount,
            "date": c.date.strftime('%Y-%m-%d'),
            "status": c.status
        } for c in contributions
    ]), 200

@contribution_bp.route('/all', methods=['GET'])
@jwt_required()
def all_contributions():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != "Admin":
        return jsonify({"error": "Admins only"}), 403

    contributions = Contribution.query.filter_by(organization_id=user.organization_id).all()
    return jsonify([
        {
            "name": c.user.name,
            "amount": c.amount,
            "date": c.date.strftime('%Y-%m-%d'),
            "status": c.status
        } for c in contributions
    ]), 200

@contribution_bp.route('/unpaid', methods=['GET'])
@jwt_required()
def unpaid_members():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != "Admin":
        return jsonify({"error": "Admins only"}), 403

    this_month = datetime.utcnow().month
    this_year = datetime.utcnow().year

    # Get all members in organization
    members = User.query.filter_by(organization_id=user.organization_id, role="Member").all()
    unpaid = []

    for member in members:
        paid = Contribution.query.filter_by(user_id=member.id).filter(
            extract('month', Contribution.date) == this_month,
            extract('year', Contribution.date) == this_year
        ).first()
        if not paid:
            unpaid.append({
                "name": member.name,
                "email": member.email
            })

    return jsonify(unpaid), 200
