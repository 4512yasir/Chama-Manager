from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, ContributionSchedule
from datetime import datetime

schedule_bp = Blueprint('schedule_bp', __name__)

@jwt_required()
@schedule_bp.route('/set', methods=['POST'])
def set_contribution_schedule():
    user = User.query.get(get_jwt_identity())
    if user.role != "Admin":
        return jsonify({"error": "Admins only"}), 403

    data = request.get_json()
    date_str = data.get("date")

    if not date_str:
        return jsonify({"error": "Date required"}), 400

    try:
        new_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Remove existing schedule for that org (optional)
    ContributionSchedule.query.filter_by(organization_id=user.organization_id).delete()

    schedule = ContributionSchedule(
        date=new_date,
        organization_id=user.organization_id
    )
    db.session.add(schedule)
    db.session.commit()

    return jsonify({"message": "Schedule updated", "date": new_date.strftime('%Y-%m-%d')}), 200

@jwt_required()
@schedule_bp.route('/next', methods=['GET'])
def get_next_contribution_date():
    user = User.query.get(get_jwt_identity())

    schedule = ContributionSchedule.query.filter_by(
        organization_id=user.organization_id
    ).order_by(ContributionSchedule.date.desc()).first()

    if not schedule:
        return jsonify({"message": "No upcoming contribution set"}), 404

    return jsonify({"next_contribution_date": schedule.date.strftime('%Y-%m-%d')}), 200
