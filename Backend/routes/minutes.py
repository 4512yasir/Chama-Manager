# === routes/minutes.py ===
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Meeting

minutes_bp = Blueprint('minutes', __name__)

# Create meeting
@minutes_bp.route('/', methods=['POST'])
@jwt_required()
def create_meeting():
    data = request.get_json()
    title = data.get('title')
    date = data.get('date')
    agenda = data.get('agenda')

    meeting = Meeting(title=title, date=date, agenda=agenda)
    db.session.add(meeting)
    db.session.commit()

    return jsonify({'msg': 'Meeting scheduled successfully'}), 201

# Get all meetings
@minutes_bp.route('/', methods=['GET'])
@jwt_required()
def list_meetings():
    meetings = Meeting.query.all()
    return jsonify([m.to_dict() for m in meetings]), 200

# Add or update minutes for a meeting
@minutes_bp.route('/<int:meeting_id>', methods=['PUT'])
@jwt_required()
def update_minutes(meeting_id):
    data = request.get_json()
    minutes = data.get('minutes')
    meeting = Meeting.query.get_or_404(meeting_id)
    meeting.minutes = minutes
    db.session.commit()
    return jsonify({'msg': 'Minutes updated successfully'}), 200
