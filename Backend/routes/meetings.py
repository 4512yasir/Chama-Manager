from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Meeting

meeting_bp = Blueprint('meeting_bp', __name__)

# Admin creates a meeting
@meeting_bp.route('/', methods=['POST'])
@jwt_required()
def create_meeting():
    data = request.get_json()
    title = data.get('title')
    date = data.get('date')
    agenda = data.get('agenda')
    
    meeting = Meeting(title=title, date=date, agenda=agenda)
    db.session.add(meeting)
    db.session.commit()

    return jsonify({'message': 'Meeting created', 'meeting': meeting.to_dict()}), 201

# Admin adds minutes to a meeting
@meeting_bp.route('/<int:id>/minutes', methods=['PUT'])
@jwt_required()
def add_minutes(id):
    data = request.get_json()
    minutes = data.get('minutes')

    meeting = Meeting.query.get_or_404(id)
    meeting.minutes = minutes
    db.session.commit()

    return jsonify({'message': 'Minutes updated', 'meeting': meeting.to_dict()})

# Get all meetings (members & admin)
@meeting_bp.route('/', methods=['GET'])
@jwt_required()
def get_meetings():
    meetings = Meeting.query.order_by(Meeting.date.desc()).all()
    return jsonify([m.to_dict() for m in meetings])
