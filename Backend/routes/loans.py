from flask import Blueprint, request, jsonify
from extension import db
from models import Loan, Report
from flask_jwt_extended import jwt_required, get_jwt_identity
from utilis.auth import role_required

loans_bp = Blueprint('loans', __name__)

# ===========================
# Member requests a loan
# ===========================
@loans_bp.route('/request/', methods=['POST'])  # ✅ Trailing slash added
@jwt_required()
@role_required('member')
def request_loan():
    user = get_jwt_identity()
    data = request.json
    new_loan = Loan(user_id=user['id'], amount=data['amount'], reason=data.get('reason', 'Not provided'))
    db.session.add(new_loan)
    db.session.commit()
    return jsonify(message='Loan requested successfully')

# ===========================
# Admin/Treasurer views all loans
# ===========================
@loans_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('admin', 'treasurer')
def view_loans():
    loans = Loan.query.all()
    return jsonify([
        {
            'id': l.id,
            'member_id': l.user_id,
            'amount': l.amount,
            'status': l.status,
            'reason': l.reason
        } for l in loans
    ])

# ===========================
# Admin/Treasurer views loans for a specific member
# ===========================
@loans_bp.route('/member/<int:member_id>/', methods=['GET'])
@jwt_required()
@role_required('admin', 'treasurer')
def get_member_loans(member_id):
    loans = Loan.query.filter_by(user_id=member_id).all()
    if loans:
        return jsonify([{
            'id': loan.id,
            'amount': loan.amount,
            'status': loan.status,
            'reason': loan.reason
        } for loan in loans])
    return jsonify(message='No loans found for this member'), 404

# ===========================
# Member views their own loans
# ===========================
@loans_bp.route('/my-loans/', methods=['GET'])  # ✅ Trailing slash confirmed
@jwt_required()
@role_required('member')
def get_my_loans():
    user = get_jwt_identity()
    loans = Loan.query.filter_by(user_id=user['id']).all()

    return jsonify([{
        'id': loan.id,
        'amount': loan.amount,
        'status': loan.status,
        'reason': loan.reason
    } for loan in loans])

# ===========================
# Member updates their loan request (only if pending)
# ===========================
@loans_bp.route('/<int:id>/', methods=['PUT'])  # ✅ Update route added
@jwt_required()
@role_required('member')
def update_loan(id):
    user = get_jwt_identity()
    loan = Loan.query.filter_by(id=id, user_id=user['id']).first()

    if not loan:
        return jsonify(message='Loan not found'), 404

    if loan.status != 'pending':
        return jsonify(message='Only pending loans can be updated'), 400

    data = request.json
    loan.amount = data['amount']
    loan.reason = data.get('reason', loan.reason)
    db.session.commit()

    return jsonify(message='Loan updated successfully')

# ===========================
# Member deletes their loan request (only if pending)
# ===========================
@loans_bp.route('/delete/<int:id>/', methods=['DELETE'])  # ✅ Delete route added
@jwt_required()
@role_required('member')
def delete_loan(id):
    user = get_jwt_identity()
    loan = Loan.query.filter_by(id=id, user_id=user['id']).first()

    if not loan:
        return jsonify(message='Loan not found'), 404

    if loan.status != 'pending':
        return jsonify(message='Only pending loans can be deleted'), 400

    db.session.delete(loan)
    db.session.commit()

    return jsonify(message='Loan deleted successfully')

# ===========================
# Approve loan
# ===========================
@loans_bp.route('/approve/<int:id>/', methods=['POST'])
@jwt_required()
@role_required('admin', 'treasurer')
def approve_loan(id):
    loan = Loan.query.get(id)
    if loan:
        loan.status = 'approved'
        db.session.commit()

        report = Report(
            type='Loan Approved',
            description=f'Loan of Ksh {loan.amount} for member ID {loan.user_id} was approved.'
        )
        db.session.add(report)
        db.session.commit()

        return jsonify(message='Loan approved successfully')
    return jsonify(message='Loan not found'), 404

# ===========================
# Reject loan
# ===========================
@loans_bp.route('/reject/<int:id>/', methods=['POST'])
@jwt_required()
@role_required('admin', 'treasurer')
def reject_loan(id):
    loan = Loan.query.get(id)
    if loan:
        loan.status = 'rejected'
        db.session.commit()

        report = Report(
            type='Loan Rejected',
            description=f'Loan of Ksh {loan.amount} for member ID {loan.user_id} was rejected.'
        )
        db.session.add(report)
        db.session.commit()

        return jsonify(message='Loan rejected successfully')
    return jsonify(message='Loan not found'), 404
