from flask import Blueprint, jsonify
from models import Report
from flask_jwt_extended import jwt_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['GET'])
@jwt_required()
def get_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'type': r.type,
        'description': r.description,
        'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for r in reports])
