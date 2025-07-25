# loans.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Loan, User

loan_bp = Blueprint('loan', __name__, url_prefix='/loan')


@loan_bp.route('/request', methods=['POST'])
@jwt_required()
def request_loan():
    data = request.get_json()
    amount = data.get('amount')
    reason = data.get('reason')

    if not amount or not reason:
        return jsonify({'error': 'Missing amount or reason'}), 400

    current_user_id = get_jwt_identity()['id']
    loan = Loan(amount=amount, reason=reason, user_id=current_user_id)

    db.session.add(loan)
    db.session.commit()
    return jsonify({'message': 'Loan request submitted'}), 201


@loan_bp.route('/my-loans', methods=['GET'])
@jwt_required()
def my_loans():
    current_user_id = get_jwt_identity()['id']
    loans = Loan.query.filter_by(user_id=current_user_id).all()
    return jsonify([{
        'id': loan.id,
        'amount': loan.amount,
        'reason': loan.reason,
        'status': loan.status,
        'created_at': loan.created_at
    } for loan in loans]), 200


@loan_bp.route('/approve/<int:loan_id>', methods=['PUT'])
@jwt_required()
def approve_loan(loan_id):
    user = User.query.get(get_jwt_identity()['id'])

    if user.role not in ['admin', 'system_operator']:
        return jsonify({'error': 'Unauthorized'}), 403

    loan = Loan.query.get_or_404(loan_id)
    loan.status = 'approved'
    db.session.commit()
    return jsonify({'message': 'Loan approved'}), 200


@loan_bp.route('/reject/<int:loan_id>', methods=['PUT'])
@jwt_required()
def reject_loan(loan_id):
    user = User.query.get(get_jwt_identity()['id'])

    if user.role not in ['admin', 'system_operator']:
        return jsonify({'error': 'Unauthorized'}), 403

    loan = Loan.query.get_or_404(loan_id)
    loan.status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Loan rejected'}), 200


@loan_bp.route('/all', methods=['GET'])
@jwt_required()
def view_all_loans():
    user = User.query.get(get_jwt_identity()['id'])

    if user.role == 'system_operator':
        loans = Loan.query.all()
    elif user.role == 'admin':
        loans = Loan.query.join(User).filter(User.organization_id == user.organization_id).all()
    else:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify([{
        'id': loan.id,
        'amount': loan.amount,
        'status': loan.status,
        'reason': loan.reason,
        'member': loan.user.name,
        'org': loan.user.organization.name,
        'created_at': loan.created_at
    } for loan in loans]), 200
